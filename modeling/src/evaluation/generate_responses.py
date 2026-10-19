from ollama import Client
import json

client = Client(host="http://localhost:11434", timeout=160)

# cargar dataset:

#json_string = json.dumps(json_result, indent=2)

# tomar prompts y guardarlos:

prompts = ["hello", "how are you?", "tell me a joke"] # obtener solo prompts en una lista.

results = {}

for prompt in prompts:
    result = client.generate(model="llama3.1:8b", prompt=prompt, stream=False)

    json_result = result.model_dump(exclude={"context","thinking",
                                         "logprobs","image",
                                         "completed","total"})

    results[prompt] = json_result

json_string = json.dumps(results, indent=2)
print(json_string)