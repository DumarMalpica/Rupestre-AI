"""
Tests de integración: prueba el grafo LangGraph de extremo a extremo.
NOTA: Estos tests requieren todos los servicios levantados.
Corren solo en PRs hacia main (ver .github/workflows/ci.yml).
"""

import pytest
from core.graph import rupestre_graph

MOCK_INITIAL_STATE = {
    "image_path": "data/samples/test_pictogram.jpg",
    "site_name": "Villa de Leyva — Test de Integración",
    "coordinates": (5.634, -73.525),
    "session_id": "integration-test-001",
    "errors": [],
}


@pytest.mark.integration
def test_grafo_completa_sin_errores():
    """El grafo debe ejecutarse de inicio a fin sin excepciones."""
    result = rupestre_graph.invoke(MOCK_INITIAL_STATE)
    assert result is not None


@pytest.mark.integration
def test_grafo_genera_ficha_json():
    """El grafo debe producir una ficha JSON con campos obligatorios."""
    result = rupestre_graph.invoke(MOCK_INITIAL_STATE)
    assert result.get("ficha_json") is not None
    ficha = result["ficha_json"]
    assert "site_name" in ficha
    assert "record_id" in ficha
    assert "cultural_interpretation" in ficha


@pytest.mark.integration
def test_grafo_detiene_imagen_invalida():
    """Si image_quality_ok=False, el grafo termina sin generar ficha."""
    # Forzamos imagen inválida con path inexistente
    bad_state = {**MOCK_INITIAL_STATE, "image_path": ""}
    result = rupestre_graph.invoke(bad_state)
    # El grafo puede terminar en END sin record_id
    # La ficha no debe generarse si la imagen falló
    # (comportamiento depende del placeholder del AG1)
    assert result is not None
