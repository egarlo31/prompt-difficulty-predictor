from typing import Any

import requests


class OllamaClient:
    """Client for interacting with an Ollama inference server."""

    def __init__(
        self,
        base_url: str,
        timeout: int = 300,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(
        self,
        model: str,
        prompt: str,
        options: dict[str, Any] | None = None,
        stream: bool = False,
    ) -> dict[str, Any]:
        """Execute a prompt using the selected Ollama model."""

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": options or {},
        }

        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()

    def list_models(self) -> dict[str, Any]:
        """Return models currently available in Ollama."""

        response = requests.get(
            f"{self.base_url}/api/tags",
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()

    def get_version(self) -> dict[str, Any]:
        """Return the Ollama server version."""

        response = requests.get(
            f"{self.base_url}/api/version",
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()