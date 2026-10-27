from fastapi import APIRouter, HTTPException

try:
    from backend.api.schemas import (
        PredictionDetails,
        PredictionRequest,
        PredictionResponse,
    )
except ImportError:
    from api.schemas import (
        PredictionDetails,
        PredictionRequest,
        PredictionResponse,
    )

router = APIRouter(prefix="/api/v1", tags=["prediction"])


@router.get("/health")
def health_check():
    """Endpoint de verificación de estado del servicio."""
    return {
        "status": "ok",
        "service": "prompt-difficulty-predictor",
        "version": "0.1.0",
    }


@router.post("/predict", response_model=PredictionResponse)
def predict_difficulty(request: PredictionRequest):
    """
    Predice la dificultad de un prompt de programación para el modelo objetivo.

    Sigue el contrato definido en T-06 con el predictor provisional (T-08),
    previo a la integración del modelo Deep Learning final (T-24).
    """
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="El prompt de programación no puede estar vacío.",
        )

    text = prompt.lower()
    word_count = len(prompt.split())
    line_count = len(prompt.splitlines())

    hard_keywords = [
        "coq",
        "bizantino",
        "byzantine",
        "consensus",
        "np-hard",
        "lazy propagation",
        "segment tree",
        "bitmask",
        "geometry",
        "turing",
        "formal proof",
        "asynchronous",
    ]
    medium_keywords = [
        "o(n)",
        "o(log n)",
        "árbol",
        "tree",
        "grafo",
        "graph",
        "dinámica",
        "dp",
        "two sum",
        "recursivo",
        "recursive",
        "binary search",
        "hash",
        "ordenamiento",
        "sort",
    ]

    detected_hard = [k for k in hard_keywords if k in text]
    detected_medium = [k for k in medium_keywords if k in text]

    # Heurística experimental para el clasificador provisional
    if (
        any(k in text for k in ["bizantino", "byzantine", "coq", "formal proof"])
        or word_count > 160
    ):
        difficulty = "Cannot Solve"
        confidence = 0.92
        success_rate = 0.0
        description = (
            "El prompt excede las capacidades de razonamiento o verificación de Llama 3 8B. "
            "Tasa de éxito nula bajo la suite de pruebas automatizadas."
        )
    elif detected_hard or word_count > 80:
        difficulty = "Hard"
        confidence = 0.85
        success_rate = 22.5
        description = (
            "Alta complejidad algorítmica. Llama 3 8B presenta una tasa baja de resolución "
            "satisfactoria en la primera pasada de generación de código."
        )
    elif not detected_medium and word_count < 35:
        difficulty = "Easy"
        confidence = 0.95
        success_rate = 94.0
        description = (
            "Tarea algorítmica elemental o estándar. Llama 3 8B genera código funcional "
            "que aprueba los casos de prueba con alta probabilidad."
        )
    else:
        difficulty = "Medium"
        confidence = 0.88
        success_rate = 65.0
        description = (
            "Complejidad algorítmica intermedia. Llama 3 8B resuelve la tarea "
            "con consideraciones típicas de estructuras de datos y lógica."
        )

    return PredictionResponse(
        difficulty=difficulty,
        confidence=confidence,
        estimated_success_rate=success_rate,
        model_target=request.model_target or "Llama 3 8B",
        details=PredictionDetails(
            description=description,
            word_count=word_count,
            line_count=line_count,
            features_detected=detected_hard + detected_medium,
        ),
    )
