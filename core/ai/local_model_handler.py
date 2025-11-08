import requests
import subprocess


class LocalModelHandler:
    def __init__(self, backend="lmstudio", model_name=None, lmstudio_url="http://127.0.0.1:1234", ollama_url="http://127.0.0.1:11434"):
        self.backend = backend.lower()
        self.model_name = model_name
        self.lmstudio_url = lmstudio_url
        self.ollama_url = ollama_url

    def chunk_text(self, text, chunk_size=512):
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    def query_lmstudio(self, prompt):
        payload = {
            "prompt": prompt,
            "model": self.model_name or "default"
        }
        try:
            response = requests.post(f"{self.lmstudio_url}/v1/completions", json=payload)
            response.raise_for_status()
            json_resp = response.json()
            # Debug print to verify response format
            print("LM Studio completion response:", json_resp)
            # Extract text from choices
            return json_resp.get("choices", [{}])[0].get("text", "")
        except Exception as e:
            return f"[Error querying LM Studio: {e}]"

    def query_ollama(self, prompt):
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

    def query_api(self, prompt):
        return f"[API response from {self.model_name or 'default'}]"

    def local_model_response(self, prompt):
        chunks = self.chunk_text(prompt)
        responses = []

        for chunk in chunks:
            if self.backend == "lmstudio":
                res = self.query_lmstudio(chunk)
            elif self.backend == "ollama":
                raw = self.query_ollama(chunk)
                if isinstance(raw, dict) and "content" in raw:
                    res = raw["content"]
                elif isinstance(raw, list):
                    res = " ".join(r.get("content", "") for r in raw)
                else:
                    res = str(raw)
            else:
                res = f"[Unknown backend: {self.backend}]"

            responses.append(res.strip())

        return " ".join(responses)

    def detect_models(self):
        models = {}

        # LM Studio detection
        try:
            response = requests.get(f"{self.lmstudio_url}/v1/models", timeout=2)
            if response.status_code == 200:
                data = response.json()
                # The actual models list is inside data['data']
                for model in data.get("data", []):
                    model_name = model.get("id", str(model))
                    models[f"LM Studio: {model_name}"] = model_name
        except Exception as e:
            print("LM Studio API detection failed:", e)

        # Ollama detection
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            lines = result.stdout.splitlines()

            # Skip header if it exists (check if first line contains 'NAME')
            if lines and "NAME" in lines[0]:
                lines = lines[1:]

            for line in lines:
                if line.strip():
                    # Extract the first column (model name) by splitting whitespace
                    model_name = line.split()[0]
                    models[f"Ollama: {model_name}"] = model_name
        except Exception as e:
            print("Ollama detection failed:", e)

        return models

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
