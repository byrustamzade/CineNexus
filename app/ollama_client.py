import requests

from app.settings import OLLAMA_MODEL


class OllamaClient:
    def __init__(self, model: str = OLLAMA_MODEL, base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def generate(self, prompt: str) -> str:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=300,
        )

        response.raise_for_status()
        return response.json()["response"].strip()