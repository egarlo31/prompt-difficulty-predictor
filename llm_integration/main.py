from fastapi import FastAPI
from llm_integration.api.endpoints import router

app = FastAPI(title="LLM Integration API")

app.include_router(router)
