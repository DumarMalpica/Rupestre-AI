"""Tests independientes para AG3 — Iconographic Comparator."""

import pytest
from agents.iconographic_comparator.agent import comparator_node

MOCK_STATE = {
    "image_path": "data/samples/test_pictogram.jpg",
    "site_name": "Villa de Leyva - Sector Norte",
    "coordinates": (5.634, -73.525),
    "session_id": "test-session-001",
    "errors": [],
}


MOCK_STATE_WITH_MOTIFS = {
    **MOCK_STATE,
    "enhanced_image": "data/samples/test_pictogram.jpg",
    "image_quality_ok": True,
    "detected_motifs": [
        {"id": "motif_001", "clase": "espiral", "confidence": 0.91, "bbox": [100, 150, 300, 350]}
    ],
    "motif_count": 1,
}

def test_retorna_similar_motifs():
    """El agente debe retornar la lista de motivos similares."""
    result = comparator_node(MOCK_STATE_WITH_MOTIFS)
    assert "similar_motifs" in result
    assert isinstance(result["similar_motifs"], list)

def test_retorna_flag_regional_parallels():
    """Debe retornar el flag has_regional_parallels como bool."""
    result = comparator_node(MOCK_STATE_WITH_MOTIFS)
    assert "has_regional_parallels" in result
    assert isinstance(result["has_regional_parallels"], bool)

def test_scores_en_rango_valido():
    """Los scores de similitud deben estar entre 0 y 1."""
    result = comparator_node(MOCK_STATE_WITH_MOTIFS)
    for motif in result["similar_motifs"]:
        for match in motif.get("top_matches", []):
            assert 0.0 <= match["score"] <= 1.0

def test_sin_motivos_no_rompe_agente():
    """Con lista de motivos vacía no debe lanzar excepción."""
    state = {**MOCK_STATE_WITH_MOTIFS, "detected_motifs": [], "motif_count": 0}
    result = comparator_node(state)
    assert "similar_motifs" in result
