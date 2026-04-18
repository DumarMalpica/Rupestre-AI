"""Tests independientes para AG1 — Image Processor."""

import pytest
from agents.image_processor.agent import image_processor_node

MOCK_STATE = {
    "image_path": "data/samples/test_pictogram.jpg",
    "site_name": "Villa de Leyva - Sector Norte",
    "coordinates": (5.634, -73.525),
    "session_id": "test-session-001",
    "errors": [],
}


def test_imagen_valida_retorna_quality_ok():
    """Una imagen válida debe retornar image_quality_ok=True."""
    result = image_processor_node(MOCK_STATE)
    assert result["image_quality_ok"] is True

def test_resultado_contiene_enhanced_image():
    """El agente debe retornar la ruta de la imagen procesada."""
    result = image_processor_node(MOCK_STATE)
    assert "enhanced_image" in result
    assert result["enhanced_image"] is not None

def test_no_modifica_campos_de_otros_agentes():
    """El agente solo debe escribir sus campos, no los de otros."""
    result = image_processor_node(MOCK_STATE)
    assert "detected_motifs" not in result
    assert "cultural_interpretation" not in result

def test_imagen_inexistente_no_rompe_pipeline():
    """Si la imagen no existe, debe manejar el error sin excepción no controlada."""
    bad_state = {**MOCK_STATE, "image_path": "no_existe.jpg"}
    result = image_processor_node(bad_state)
    # Debe retornar algo (aunque sea con calidad False)
    assert "image_quality_ok" in result
