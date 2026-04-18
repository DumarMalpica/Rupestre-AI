"""Tests independientes para AG2 — Motif Detector."""

import pytest
from agents.motif_detector.agent import motif_detector_node

MOCK_STATE = {
    "image_path": "data/samples/test_pictogram.jpg",
    "site_name": "Villa de Leyva - Sector Norte",
    "coordinates": (5.634, -73.525),
    "session_id": "test-session-001",
    "errors": [],
}


MOCK_STATE_WITH_IMAGE = {
    **MOCK_STATE,
    "enhanced_image": "data/samples/test_pictogram.jpg",
    "image_quality_ok": True,
}

def test_retorna_lista_de_motivos():
    """El agente debe retornar una lista (puede estar vacía)."""
    result = motif_detector_node(MOCK_STATE_WITH_IMAGE)
    assert "detected_motifs" in result
    assert isinstance(result["detected_motifs"], list)

def test_motif_count_coincide_con_lista():
    """motif_count debe ser igual a len(detected_motifs)."""
    result = motif_detector_node(MOCK_STATE_WITH_IMAGE)
    assert result["motif_count"] == len(result["detected_motifs"])

def test_cada_motivo_tiene_campos_requeridos():
    """Cada motivo detectado debe tener id, clase, confidence y bbox."""
    result = motif_detector_node(MOCK_STATE_WITH_IMAGE)
    for motif in result["detected_motifs"]:
        assert "id" in motif
        assert "clase" in motif
        assert "confidence" in motif
        assert "bbox" in motif

def test_confidence_en_rango_valido():
    """El confidence de cada motivo debe estar entre 0 y 1."""
    result = motif_detector_node(MOCK_STATE_WITH_IMAGE)
    for motif in result["detected_motifs"]:
        assert 0.0 <= motif["confidence"] <= 1.0
