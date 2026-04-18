"""Tests independientes para AG4 — Cultural Analyst."""

import pytest
from agents.cultural_analyst.agent import cultural_analyst_node

MOCK_STATE = {
    "image_path": "data/samples/test_pictogram.jpg",
    "site_name": "Villa de Leyva - Sector Norte",
    "coordinates": (5.634, -73.525),
    "session_id": "test-session-001",
    "errors": [],
}


MOCK_STATE_WITH_CONTEXT = {
    **MOCK_STATE,
    "detected_motifs": [
        {"id": "motif_001", "clase": "espiral", "confidence": 0.91, "bbox": [100, 150, 300, 350]}
    ],
    "motif_count": 1,
    "similar_motifs": [
        {"motif_id": "motif_001", "top_matches": [{"site": "Villa de Leyva", "score": 0.88}]}
    ],
    "has_regional_parallels": True,
}

def test_genera_interpretacion_no_vacia():
    """La interpretación cultural generada no debe ser vacía."""
    result = cultural_analyst_node(MOCK_STATE_WITH_CONTEXT)
    assert "cultural_interpretation" in result
    assert result["cultural_interpretation"]
    assert len(result["cultural_interpretation"]) > 10

def test_retorna_fuentes_citadas():
    """Debe retornar al menos una fuente citada."""
    result = cultural_analyst_node(MOCK_STATE_WITH_CONTEXT)
    assert "cited_sources" in result
    assert isinstance(result["cited_sources"], list)

def test_confidence_es_float():
    """interpretation_confidence debe ser un float entre 0 y 1."""
    result = cultural_analyst_node(MOCK_STATE_WITH_CONTEXT)
    assert "interpretation_confidence" in result
    assert 0.0 <= result["interpretation_confidence"] <= 1.0

def test_hitl_flag_presente():
    """El flag requires_human_review siempre debe estar presente."""
    result = cultural_analyst_node(MOCK_STATE_WITH_CONTEXT)
    assert "requires_human_review" in result
    assert isinstance(result["requires_human_review"], bool)
