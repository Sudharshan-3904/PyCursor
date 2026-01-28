"""
Local AI Model Management Module.
Facilitates communication with local LLM backends (Ollama, LM Studio) using 
RESTful APIs and system-level discovery.
"""

import requests
import subprocess
from core.utilities.utils import load_systemPrompt

class LocalModelHandler:
    """
    Interface for interacting with locally hosted Large Language Models.
    Abstracts the implementation differences between Ollama and OpenAI-compatible
    backends like LM Studio.
    """
    def __init__(self, backend="ollama", model_name=None, lmstudio_url="http://127.0.0.1:1234", ollama_url="http://127.0.0.1:11434"):
        """
        Initializes the handler with target backend configuration.
        """
        self.backend = backend.lower()
        self.model_name = model_name
        self.lmstudio_url = lmstudio_url
        self.ollama_url = ollama_url
        self.system_prompt = {"role": "system", "content": load_systemPrompt()}

    def _chunk_text(self, text: str, chunk_size: int = 2048) -> list:
        """
        Internal utility to split large prompts into manageable pieces to avoid context overflow.
        """
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    def query_lmstudio(self, prompt: str) -> str:
        """
        Executes a completion request against an LM Studio (OpenAI-compatible) endpoint.
        """
        payload = {
            "messages": [self.system_prompt, {"role": "user", "content": prompt}],
            "model": self.model_name or "default"
        }
        try:
            resp = requests.post(f"{self.lmstudio_url}/v1/chat/completions", json=payload, timeout=30)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[LM Studio Error]: {e}"

    def query_ollama(self, prompt: str) -> str:
        """
        Executes a completion request against the Ollama chat API.
        """
        payload = {
            "model": self.model_name or "granite3.1-moe:latest",
            "messages": [self.system_prompt, {"role": "user", "content": prompt}],
            "stream": False
        }
        try:
            resp = requests.post(f"{self.ollama_url}/api/chat", json=payload, timeout=30)
            resp.raise_for_status()
            return resp.json().get("message", {}).get("content", "")
        except Exception as e:
            return f"[Ollama Error]: {e}"

    def local_model_response(self, prompt: str) -> str:
        """
        Orchestrates request chunking and backend-specific querying.
        """
        chunks = self._chunk_text(prompt)
        results = []

        for chunk in chunks:
            if self.backend == "lmstudio":
                res = self.query_lmstudio(chunk)
            elif self.backend == "ollama":
                res = self.query_ollama(chunk)
            else:
                res = f"[Error]: Active backend '{self.backend}' is not supported."
            results.append(res.strip())

        return " ".join(results)

    def detect_models(self) -> dict:
        """
        Discovers locally running models by polling API endpoints and system binaries.
        Returns a dictionary of human-readable labels and model identifiers.
        """
        discovered = {}

        # 1. Inspect LM Studio (OpenAI compatible list endpoint)
        try:
            resp = requests.get(f"{self.lmstudio_url}/v1/models", timeout=2)
            if resp.status_code == 200:
                for m in resp.json().get("data", []):
                    name = m.get("id")
                    discovered[f"LM Studio: {name}"] = name
        except Exception:
            pass

        # 2. Inspect Ollama (system command)
        try:
            proc = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=False)
            lines = proc.stdout.splitlines()
            if len(lines) > 1: # Skip header
                for line in lines[1:]:
                    if line.strip():
                        name = line.split()[0]
                        discovered[f"Ollama: {name}"] = name
        except Exception:
            pass

        return discovered
