import os
import faiss
import numpy as np
import pickle
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer

class RAGManager:
    """
    Manages local vector database for code search using FAISS and Sentence-Transformers.
    """
    def __init__(self, project_path: str, index_dir: str = ".pycursor/rag"):
        self.project_path = project_path
        self.index_dir = os.path.join(project_path, index_dir)
        self.index_file = os.path.join(self.index_dir, "index.faiss")
        self.metadata_file = os.path.join(self.index_dir, "metadata.pkl")
        
        # Initialize model (all-MiniLM-L6-v2 is small and fast)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        self.index = None
        self.metadata = [] # List of {path, snippet, line_start}
        
        self._ensure_dir()
        self._load_index()

    def _ensure_dir(self):
        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir, exist_ok=True)

    def _load_index(self):
        if os.path.exists(self.index_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.metadata_file, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)

    def _save_index(self):
        faiss.write_index(self.index, self.index_file)
        with open(self.metadata_file, "wb") as f:
            pickle.dump(self.metadata, f)

    def add_documents(self, file_path: str, content: str):
        """
        Chunks the file content and adds it to the index.
        """
        self.remove_document(file_path)
        
        rel_path = os.path.relpath(file_path, self.project_path).replace("\\", "/")
        lines = content.splitlines()
        chunk_size = 20
        new_entries = []
        
        for i in range(0, len(lines), chunk_size):
            snippet = "\n".join(lines[i:i+chunk_size])
            if not snippet.strip(): continue
            
            new_entries.append({
                "path": rel_path,
                "snippet": snippet,
                "line_start": i + 1
            })
        
        if new_entries:
            snippets = [e["snippet"] for e in new_entries]
            embeddings = self.model.encode(snippets)
            self.index.add(np.array(embeddings).astype('float32'))
            self.metadata.extend(new_entries)
            self._save_index()

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Performs vector search for the query.
        """
        if self.index.ntotal == 0:
            return []
            
        query_embedding = self.model.encode([query])[0]
        distances, indices = self.index.search(np.array([query_embedding]).astype('float32'), top_k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.metadata):
                results.append(self.metadata[idx])
        return results

    def remove_document(self, file_path: str):
        """
        Removes all snippets associated with a specific file from the index and metadata.
        Note: FAISS IndexFlatL2 doesn't support easy removal by ID without rebuilding.
        For simplicity in this version, we'll rebuild the index if metadata is large, 
        or just filter during search.
        """
        rel_path = os.path.relpath(file_path, self.project_path).replace("\\", "/")
        self.metadata = [m for m in self.metadata if m["path"] != rel_path]
        # Rebuilding index (inefficient but safe for Phase 1)
        self._rebuild_index()

    def _rebuild_index(self):
        self.index = faiss.IndexFlatL2(self.dimension)
        if not self.metadata:
            self._save_index()
            return
            
        snippets = [m["snippet"] for m in self.metadata]
        embeddings = self.model.encode(snippets)
        self.index.add(np.array(embeddings).astype('float32'))
        self._save_index()

    def index_project(self):
        """
        Walks the project and indexes all supported files in parallel threads.
        """
        from core.ai.context_manager import ContextManager
        from concurrent.futures import ThreadPoolExecutor
        
        cm = ContextManager(self.project_path)
        files = cm._list_project_files()
        
        def process_file(rel_path):
            abs_path = os.path.join(self.project_path, rel_path)
            content = cm._read_safe(abs_path)
            if content:
                # Prepare entries but don't add to index yet (index isn't thread-safe for adding)
                rel_p = rel_path.replace("\\", "/")
                lines = content.splitlines()
                chunk_size = 30 # Increased chunk size for better context
                entries = []
                for i in range(0, len(lines), chunk_size):
                    snippet = "\n".join(lines[i:i+chunk_size])
                    if snippet.strip():
                        entries.append({
                            "path": rel_p,
                            "snippet": snippet,
                            "line_start": i + 1
                        })
                return entries
            return []

        all_new_entries = []
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            results = list(executor.map(process_file, files))
            for res in results:
                all_new_entries.extend(res)

        if all_new_entries:
            # Batch add to index for efficiency
            self.metadata = all_new_entries
            self._rebuild_index()
