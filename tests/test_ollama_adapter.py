from llm_integration.local_llm.ollama_adapter import OllamaAdapter

llm = OllamaAdapter(model="llama3.1:8b")

response = llm.generate("Dame un script sencillo de una funcion recursiva")

print(response)
