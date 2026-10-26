"""The single Ollama generation API used by the backend and evaluation."""
from ollama import Client


class OllamaAdapter:
    def __init__(self, model, host="http://localhost:11434", *, timeout=160,
                 options=None, keep_alive="10m", client=None, system=None, think=None):
        self.host = host
        self.system = system
        self.think = think
        self.model = model
        self.client = client if client is not None else Client(host=host, timeout=timeout)
        self.options = dict(options or {})
        self.keep_alive = keep_alive

    def generate(self, prompt, *, options=None):
        """Return Ollama's complete response; access `.response` for text.

        Per-call overrides do not change the adapter's default options.
        Connection and inference errors propagate to the caller.
        """
        request = {}
        if self.system is not None:
            request["system"] = self.system
        if self.think is not None:
            request["think"] = self.think
        return self.client.generate(
            model=self.model, prompt=prompt, stream=False,
            options={**self.options, **(options or {})}, keep_alive=self.keep_alive, **request,
        )
