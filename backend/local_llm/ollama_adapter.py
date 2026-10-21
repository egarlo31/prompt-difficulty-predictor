from ollama import Client


class OllamaAdapter:

    def __init__(self, model, host: str = "http://localhost:11434"):
        self.model = model
        self.client = Client(host=host, timeout=160)

    def generate(self, prompt):

        result = self.client.generate(
            model=self.model,
            prompt=prompt,
            stream=False,
            keep_alive="10m",
        )

        return result.response
