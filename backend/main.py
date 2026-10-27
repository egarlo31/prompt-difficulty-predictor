import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

try:
    from backend.api.endpoints import router
except ImportError:
    from api.endpoints import router

app = FastAPI(
    title="Prompt Difficulty Predictor API",
    description="API para estimar la dificultad de prompts de programación para Llama 3 8B",
    version="0.1.0",
)

# CORS para permitir peticiones desde servidores de desarrollo locales del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Montar el frontend para servicio unificado
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_dir = os.path.join(base_dir, "frontend")

if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
