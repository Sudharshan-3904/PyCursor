"""
AI Context Retrieval and Filtering System.
Analyzes user queries to identify relevant project files, extracts their content,
and formats it into a structured prompt context for the AI engine.
Supports explicit file mentions (@filename) and heuristic keyword matching.
"""

import os
import fnmatch
import re
import difflib
from typing import Optional

class ContextManager:
    """
    Manages the lifecycle of project-specific context provided to the LLM.
    Handles recursive file system walking, pattern-based ignore filtering,
    and term-based ranking for relevant file selection.
    """
    def __init__(self, project_path=None):
        """
        Initializes the manager with a project root and default filtering rules.
        """
        self.project_path = project_path
        self.max_context_chars = 12000  # Conservative safety limit for standard LLM context windows
        
        # Files and directories to exclude from indexing or context retrieval
        self.ignore_patterns = [
            "*.pyc", "__pycache__", ".git", ".venv", "env", "node_modules", 
            "*.png", "*.jpg", "*.svg", "*.ico", "*.pdf", "*.zip", "*.bin",
            "package-lock.json", "yarn.lock"
        ]

    def set_project_path(self, path: str):
        """
        Updates the target project root for context operations.
        """
        self.project_path = path

    def get_context(self, query: str) -> dict:
        """
        Orchestrates context gathering based on the provided user query.
        Returns formatted context text and a manifest of used file paths.
        """
        if not self.project_path: return {"text": "", "files": []}

        used_files = []
        context_blocks = []
        current_size = 0
        
        # Phase 1: Explicit Mention Resolution (@file)
        explicit_filenames = self._resolve_explicit_mentions(query)
        for rel_path in explicit_filenames:
            content = self._read_safe(os.path.join(self.project_path, rel_path))
            if content:
                used_files.append(rel_path)
                context_blocks.append(f"File: {rel_path}\n```\n{content}\n```")
                current_size += len(content)

        # Phase 2: Heuristic Relevance Discovery
        relevant_files = self._discover_relevant_files(query)
        for rel_path in relevant_files:
            if rel_path in used_files: continue
            
            content = self._read_safe(os.path.join(self.project_path, rel_path))
            if content and (current_size + len(content)) < self.max_context_chars:
                used_files.append(rel_path)
                context_blocks.append(f"File: {rel_path}\n```\n{content}\n```")
                current_size += len(content)

        if not context_blocks: return {"text": "", "files": []}

        final_text = "Project Context:\n\n" + "\n\n".join(context_blocks) + "\n\n"
        return {"text": final_text, "files": used_files}

    def _resolve_explicit_mentions(self, query: str) -> list:
        """
        Extracts @tagged words and attempts to resolve them to actual file paths using fuzzy matching.
        """
        mentions = re.findall(r'@([\w\./\-_]+)', query)
        if not mentions: return []
        
        all_files = self._list_project_files()
        resolved = []
        for m in mentions:
            # First pass: direct substring match
            candidates = [f for f in all_files if m.lower() in f.lower()]
            if candidates:
                # Prefer shortest path match
                resolved.append(min(candidates, key=len))
            else:
                # Second pass: token-based fuzzy similarity
                close_hits = difflib.get_close_matches(m, all_files, n=1, cutoff=0.5)
                if close_hits: resolved.append(close_hits[0])
                
        return resolved

    def _discover_relevant_files(self, query: str) -> list:
        """
        Ranks project files based on term frequency and filename overlap with the user query.
        """
        terms = [t.lower() for t in query.split() if len(t) > 3]
        if not terms: return []
            
        all_files = self._list_project_files()
        scores = {}
        
        for rel_path in all_files:
            score = 0
            fname = os.path.basename(rel_path).lower()
            
            # Filename weighted match (High priority)
            for t in terms:
                if t in fname: score += 15
            
            # Content frequency scan (Low priority per hit, capped)
            try:
                path = os.path.join(self.project_path, rel_path)
                if os.path.getsize(path) < 150000: # Skip massive files for performance
                    content = self._read_safe(path).lower()
                    for t in terms: score += min(content.count(t) * 2, 10)
            except Exception: pass

            if score > 0: scores[rel_path] = score
                
        # Return top 5 most relevant results
        sorted_hits = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [h[0] for h in sorted_hits[:5]]

    def _list_project_files(self) -> list:
        """
        Internal utility for recursive project traversal with exclusion handling.
        """
        manifest = []
        for root, dirs, files in os.walk(self.project_path):
            # Prune directory tree based on ignore rules
            dirs[:] = [d for d in dirs if not self._is_pattern_ignored(d)]
            
            for f in files:
                if not self._is_pattern_ignored(f):
                    rel = os.path.relpath(os.path.join(root, f), self.project_path)
                    manifest.append(rel.replace("\\", "/"))
        return manifest

    def _is_pattern_ignored(self, name: str) -> bool:
        """
        Logic for checking if a file or directory name matches any exclusion patterns.
        """
        return any(fnmatch.fnmatch(name, p) for p in self.ignore_patterns)

    def _read_safe(self, path: str) -> Optional[str]:
        """
        Internal wrapper for disk operations with basic safety and encoding handling.
        """
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return None
