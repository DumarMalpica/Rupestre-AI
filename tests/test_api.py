from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from api.main import app

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_graph(monkeypatch):
    """Reemplaza rupestre_graph por un stub que devuelve un resultado mínimo válido."""
    _RECORD_ID = "TESTABC1"
    _FICHA = {
        "record_id": _RECORD_ID,
        "generated_at": "2026-05-30T12:00:00",
        "site_name": "Test Site",
        "coordinates": (5.0, -74.0),
        "department": "No especificado",
        "municipality": "No especificado",
        "motif_count": 1,
        "detected_motifs": [],
        "similar_motifs": [],
        "has_regional_parallels": False,
        "cultural_interpretation": "Interpretación de prueba.",
        "cited_sources": [],
        "interpretation_confidence": 0.82,
        "reconstruction_applied": False,
        "requires_human_review": False,
        "images": {"original": "", "enhanced": "", "reconstructed": ""},
    }

    def _fake_invoke(state: dict) -> dict:
        return {
            **state,
            "image_quality_ok": True,
            "enhanced_image": state.get("image_path", ""),
            "detected_motifs": [],
            "motif_count": 1,
            "similar_motifs": [],
            "has_regional_parallels": False,
            "cultural_interpretation": "Interpretación de prueba.",
            "cited_sources": [],
            "interpretation_confidence": 0.82,
            "requires_human_review": False,
            "reconstruction_applied": False,
            "reconstructed_image": "",
            "confidence_map": None,
            "record_id": _RECORD_ID,
            "ficha_json": _FICHA,
            "ficha_pdf_path": "",  # no PDF en test (mock)
            "current_agent": "heritage_documenter",
            "errors": [],
        }

    class _FakeGraph:
        def invoke(self, state: dict) -> dict:
            return _fake_invoke(state)

    import api.routers.analysis as ar

    monkeypatch.setattr(ar, "rupestre_graph", _FakeGraph())
    return _RECORD_ID


@pytest.fixture
def test_image_bytes() -> bytes:
    """Imagen JPEG válida en memoria (no requiere archivo en disco)."""
    img = Image.new("RGB", (200, 200), color=(120, 60, 40))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_health_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_with_image(client, mock_graph, test_image_bytes, tmp_path, monkeypatch):
    import core.config as cfg

    monkeypatch.setattr(cfg.settings, "samples_dir", str(tmp_path / "samples"))
    monkeypatch.setattr(cfg.settings, "output_dir", str(tmp_path / "fichas"))

    response = client.post(
        "/api/analyze",
        data={"site_name": "Cerro Pintado Test", "latitude": "5.53", "longitude": "-73.62"},
        files={"image": ("test_rupestre.jpg", test_image_bytes, "image/jpeg")},
    )

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["record_id"], str)
    assert body["record_id"] != ""
    assert "motif_count" in body
    assert "processing_time_seconds" in body


def test_record_not_found(client):
    response = client.get("/api/records/NOEXISTE")
    assert response.status_code == 404
