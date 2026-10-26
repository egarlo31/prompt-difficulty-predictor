"""Single entry point for non-streaming Ollama inference."""
from ollama import Client


class OllamaAdapter:
    def __init__(self, model, host="http://localhost:11434", *, timeout=160,
                 options=None, keep_alive="10m", client=None):
        self.model = model
        self.client = client if client is not None else Client(host=host, timeout=timeout)
        self.options = dict(options or {})
        self.keep_alive = keep_alive

    def generate_result(self, prompt, *, options=None):
        """Return the full response, retaining timings for evaluation."""
        return self.client.generate(
            model=self.model, prompt=prompt, stream=False,
            options={**self.options, **(options or {})}, keep_alive=self.keep_alive,
        )

    def generate(self, prompt, *, options=None):
        """Return only generated text for existing callers."""
        return self.generate_result(prompt, options=options).response

    def warm_up(self):
        return self.generate_result("Warm-up.", options={"num_predict": 1})
