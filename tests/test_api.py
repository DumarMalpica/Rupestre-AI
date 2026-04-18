"""Tests de la API FastAPI."""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_check():
    """El endpoint /health debe responder 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_docs_disponibles():
    """Swagger UI debe estar disponible."""
    response = client.get("/api/docs")
    assert response.status_code == 200
