import requests


class LocalModelHandler:
    def __init__(self, backend="lmstudio", model_name=None, lmstudio_url="http://127.0.0.1:7860", ollama_url="http://127.0.0.1:11434"):
        """
        Initialize the local model handler.

        Args:
            backend (str): "lmstudio" or "ollama"
            model_name (str, optional): Model to use. Defaults to None (use default model).
            lmstudio_url (str): LM Studio API URL.
            ollama_url (str): Ollama API URL.
        """
        self.backend = backend.lower()
        self.model_name = model_name
        self.lmstudio_url = lmstudio_url
        self.ollama_url = ollama_url

    def chunk_text(self, text, chunk_size=512):
        """
        Split text into smaller chunks.

        Args:
            text (str): Text to chunk.
            chunk_size (int): Max characters per chunk.

        Returns:
            List[str]: List of text chunks.
        """
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    def query_lmstudio(self, prompt):
        """
        Query LM Studio API for a prompt.

        Args:
            prompt (str): Text prompt.

        Returns:
            str: Generated text.
        """
        payload = {
            "prompt": prompt,
            "model": self.model_name or "default"
        }
        try:
            response = requests.post(f"{self.lmstudio_url}/v1/completions", json=payload)
            response.raise_for_status()
            return response.json().get("text", "")
        except Exception as e:
            return f"[Error querying LM Studio: {e}]"

    def query_ollama(self, prompt):
        """
        Query Ollama API for a single prompt using /api/chat.
        """
        payload = {
            "model": self.model_name or "granite3.1-moe:latest",
            "prompt": prompt,
            "max_tokens": 500
        }
        try:
            response = requests.post(f"{self.ollama_url}/api/chat", json=payload)
            response.raise_for_status()
            return response.json().get("message", "")
        except Exception as e:
            return f"[Error querying Ollama: {e}]"

    def local_model_response(self, prompt):
        """
        Get a response from the selected local model.

        Args:
            prompt (str): Input prompt.

        Returns:
            str: Model response.
        """
        chunks = self.chunk_text(prompt)
        responses = []
        for chunk in chunks:
            if self.backend == "lmstudio":
                res = self.query_lmstudio(chunk)
            elif self.backend == "ollama":
                res = self.query_ollama(chunk)
            else:
                res = f"[Unknown backend: {self.backend}]"
            responses.append(res)
        return " ".join(responses)


def main():
    print("=== Local Model Interface ===")
    backend = input("Choose backend (lmstudio / ollama): ").strip().lower()
    model_name = input("Enter model name (leave empty for default): ").strip() or None

    handler = LocalModelHandler(backend=backend, model_name=model_name)
    while True:
        prompt = input("\nEnter prompt (or 'exit' to quit): ")
        if prompt.lower() in ["exit", "quit"]:
            break
        response = handler.local_model_response(prompt)
        print("\n=== Model Response ===")
        print(response)


if __name__ == "__main__":
    main()
