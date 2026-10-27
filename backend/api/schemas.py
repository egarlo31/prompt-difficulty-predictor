from typing import List, Optional
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Esquema de solicitud para predecir la dificultad de un prompt."""
    prompt: str = Field(
        ...,
        description="Texto del prompt de programación o problema algorítmico",
        min_length=1,
    )
    model_target: Optional[str] = Field(
        "llama3-8b",
        description="Modelo objetivo para la evaluación de dificultad",
    )


class PredictionDetails(BaseModel):
    """Detalles analíticos del prompt analizado."""
    description: str = Field(..., description="Explicación del veredicto de dificultad")
    word_count: int = Field(..., description="Cantidad de palabras en el prompt")
    line_count: int = Field(..., description="Cantidad de líneas en el prompt")
    features_detected: List[str] = Field(
        default_factory=list,
        description="Palabras clave o características identificadas",
    )


class PredictionResponse(BaseModel):
    """Esquema de respuesta con la clasificación de dificultad y métricas."""
    difficulty: str = Field(
        ...,
        description="Categoría de dificultad: Easy, Medium, Hard, Cannot Solve",
    )
    confidence: float = Field(
        ...,
        description="Nivel de confianza de la predicción (0.0 - 1.0)",
        ge=0.0,
        le=1.0,
    )
    estimated_success_rate: float = Field(
        ...,
        description="Tasa de éxito esperada en porcentaje (0.0 - 100.0)",
        ge=0.0,
        le=100.0,
    )
    model_target: str = Field(..., description="Modelo de referencia evaluado")
    details: PredictionDetails
