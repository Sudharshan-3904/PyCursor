"""
AI Context Manager Module

This module is responsible for retrieving relevant code context from the user's project
to enhance the AI assistant's responses. It supports explicit file mentions (e.g., @main.py)
and heuristic-based file retrieval.
"""
import os
import fnmatch

class ContextManager:
    """
    Manages the retrieval of file context for the AI.
    
    This class scans the project directory, filters ignored files, and retrieves
    file content based on user queries or explicit mentions. It ensures the
    AI has the necessary code snippets to understand the user's request.
    """
    def __init__(self, project_path=None):
        self.project_path = project_path
        self.max_context_length = 8000  # Character limit for context to avoid overflowing context window
        
        # Files to ignore
        self.ignore_patterns = [
            "*.pyc", "__pycache__", ".git", ".venv", "env", "node_modules", 
            "*.png", "*.jpg", "*.svg", "*.ico", "*.pdf", "*.zip",
            "package-lock.json", "yarn.lock"
        ]

    def set_project_path(self, path):
        self.project_path = path

    def get_context(self, query: str) -> dict:
        """
        Analyze query and retrieve relevant context.
        Returns a dict with: 'text' (formatted context), 'files' (list of file paths used)
        """
        if not self.project_path:
            return {"text": "", "files": []}

        used_files = []
        context_parts = []
        
        # 1. Handle explicit @filename references
        explicit_files = self._extract_file_mentions(query)
        for rel_path in explicit_files:
            file_path = os.path.join(self.project_path, rel_path)
            content = self._read_file(file_path)
            if content:
                used_files.append(rel_path)
                context_parts.append(f"File: {rel_path}\n```\n{content}\n```")

        # 2. Smart content search (Basic Keyword Matching)
        # If no explicit files, or just to augment, search for query terms in filenames
        # (A full semantic search would is better but requires embeddings)
        # 2. Smart content search (Content & Keyword)
        # Always run this to find related files not explicitly mentioned
        keyword_files = self._find_relevant_files_by_keyword(query)
        for rel_path in keyword_files:
            if rel_path not in used_files: # Avoid duplicates
                file_path = os.path.join(self.project_path, rel_path)
                content = self._read_file(file_path)
                if content:
                    # Simple budget check
                    if sum(len(c) for c in context_parts) + len(content) < self.max_context_length:
                        used_files.append(rel_path)
                        context_parts.append(f"File: {rel_path}\n```\n{content}\n```")

        if not context_parts:
            return {"text": "", "files": []}

        formatted_context = "Context from project files:\n\n" + "\n\n".join(context_parts) + "\n\n"
        return {"text": formatted_context, "files": used_files}

    def _extract_file_mentions(self, query: str) -> list:
        """Extract words starting with @ and find the closest matching file"""
        mentions = []
        import re
        # Find pattern @something
        matches = re.findall(r'@([\w\./\-_]+)', query)
        
        all_files = self._list_all_files()
        
        for match in matches:
            # Try to find exact or fuzzy match
            best_match = self._find_best_match(match, all_files)
            if best_match:
                mentions.append(best_match)
        
        return mentions

    def _find_relevant_files_by_keyword(self, query: str) -> list:
        """
        Find files relevant to the query by checking filenames AND content.
        Uses a simple scoring system:
        - Keyword in filename: 10 points
        - Keyword in content: 1 point per occurrence (capped)
        """
        keywords = [k.lower() for k in query.split() if len(k) > 3]
        if not keywords:
            return []
            
        all_files = self._list_all_files()
        scores = {}
        
        for rel_path in all_files:
            score = 0
            filename = os.path.basename(rel_path).lower()
            
            # 1. Check filename
            for k in keywords:
                if k in filename:
                    score += 10
            
            # 2. Check content (if file is text and not too huge)
            # We skip content check if filename matched strongly to save time, 
            # or we can do it to refine ranking.
            try:
                full_path = os.path.join(self.project_path, rel_path)
                # Skip large files > 100KB to maintain speed
                if os.path.getsize(full_path) < 100 * 1024:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        for k in keywords:
                            count = content.count(k)
                            score += min(count, 5) # Cap at 5 points per keyword
            except Exception:
                continue

            if score > 0:
                scores[rel_path] = score
                
        # Sort by score descending
        sorted_files = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top 3
        return [f[0] for f in sorted_files[:3]]

    def _list_all_files(self) -> list:
        """Walk project and return list of relative paths"""
        file_list = []
        for root, dirs, files in os.walk(self.project_path):
            # Filter ignored dirs
            dirs[:] = [d for d in dirs if not self._is_ignored(d)]
            
            for file in files:
                if self._is_ignored(file):
                    continue
                
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.project_path)
                file_list.append(rel_path.replace("\\", "/"))
        return file_list

    def _find_best_match(self, term: str, file_list: list) -> str:
        """Simple fuzzy match"""
        import difflib
        # 1. Exact contains
        matches = [f for f in file_list if term.lower() in f.lower()]
        if matches:
            # Prefer shortest match (likely exact filename)
            return min(matches, key=len)
        
        # 2. Difflib close match
        close = difflib.get_close_matches(term, file_list, n=1, cutoff=0.6)
        if close:
            return close[0]
            
        return None

    def _is_ignored(self, name: str) -> bool:
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False

    def _read_file(self, path: str) -> str:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
