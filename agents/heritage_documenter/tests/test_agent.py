"""Tests independientes para AG6 — Heritage Documenter."""

import pytest
from agents.heritage_documenter.agent import documenter_node

MOCK_STATE = {
    "image_path": "data/samples/test_pictogram.jpg",
    "site_name": "Villa de Leyva - Sector Norte",
    "coordinates": (5.634, -73.525),
    "session_id": "test-session-001",
    "errors": [],
}


MOCK_FULL_STATE = {
    **MOCK_STATE,
    "enhanced_image": "data/samples/test_pictogram.jpg",
    "image_quality_ok": True,
    "detected_motifs": [
        {"id": "m001", "clase": "espiral", "confidence": 0.9, "bbox": [0, 0, 100, 100]}
    ],
    "motif_count": 1,
    "similar_motifs": [],
    "has_regional_parallels": False,
    "cultural_interpretation": "Motivo asociado a la cosmología Muisca.",
    "cited_sources": [
        {"title": "Arte Rupestre Boyacá", "author": "ICANH", "year": 2018}
    ],
    "interpretation_confidence": 0.85,
    "requires_human_review": False,
    "reconstructed_image": "data/samples/test_pictogram.jpg",
    "confidence_map": None,
    "reconstruction_applied": False,
}


def test_genera_record_id():
    """Debe generar un record_id único no vacío."""
    result = documenter_node(MOCK_FULL_STATE)
    assert "record_id" in result
    assert result["record_id"]


def test_genera_ficha_json():
    """El JSON de la ficha debe contener los campos obligatorios ICANH."""
    result = documenter_node(MOCK_FULL_STATE)
    ficha = result["ficha_json"]
    assert ficha["site_name"] == MOCK_FULL_STATE["site_name"]
    assert "cultural_interpretation" in ficha
    assert "cited_sources" in ficha
    assert "motif_count" in ficha
    assert "generated_at" in ficha


def test_dos_ejecuciones_generan_ids_distintos():
    """Cada ejecución debe generar un record_id diferente."""
    r1 = documenter_node(MOCK_FULL_STATE)
    r2 = documenter_node(MOCK_FULL_STATE)
    assert r1["record_id"] != r2["record_id"]
