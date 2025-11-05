import openai
import os

class AIEngine:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        if self.api_key:
            openai.api_key = self.api_key

    def generate(self, prompt: str) -> str:
        """Send a prompt to OpenAI (or any API) and return the result."""
        if not self.api_key:
            return "[AI Disabled] Please set OPENAI_API_KEY."
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message["content"]
        except Exception as e:
            return f"[AI Error] {e}"
