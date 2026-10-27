"""Minimal Ollama transport with no experiment statistics or persistence."""

from ollama import Client


class OllamaGateway:
    def __init__(self, host="http://localhost:11434", *, timeout=160, client=None):
        self.client = (
            client if client is not None else Client(host=host, timeout=timeout)
        )

    def generate(
        self, prompt, *, model, options=None, keep_alive="10m", system=None, think=None
    ):
        request = {}
        if system is not None:
            request["system"] = system
        if think is not None:
            request["think"] = think
        return self.client.generate(
            model=model,
            prompt=prompt,
            stream=False,
            options=dict(options or {}),
            keep_alive=keep_alive,
            **request,
        )
