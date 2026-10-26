from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "prompt-difficulty-predictor"


def test_predict_endpoint_easy():
    payload = {
        "prompt": "Escribe una funcion que sume dos numeros a y b",
        "model_target": "llama3-8b",
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["difficulty"] == "Easy"
    assert data["estimated_success_rate"] > 80.0
    assert "details" in data


def test_predict_endpoint_hard():
    payload = {
        "prompt": "Implementa un segment tree con lazy propagation en C++ y bitmask dp",
        "model_target": "llama3-8b",
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["difficulty"] in ["Hard", "Cannot Solve"]


def test_predict_endpoint_empty():
    payload = {"prompt": "   "}
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422 or response.status_code == 400
