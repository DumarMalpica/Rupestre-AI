"""Tests independientes para AG5 — Reconstructor."""

import pytest
from agents.reconstructor.agent import reconstructor_node

MOCK_STATE = {
    "image_path": "data/samples/test_pictogram.jpg",
    "site_name": "Villa de Leyva - Sector Norte",
    "coordinates": (5.634, -73.525),
    "session_id": "test-session-001",
    "errors": [],
}


MOCK_STATE_FOR_RECON = {
    **MOCK_STATE,
    "enhanced_image": "data/samples/test_pictogram.jpg",
    "image_quality_ok": True,
    "detected_motifs": [
        {"id": "motif_001", "clase": "espiral", "confidence": 0.91, "bbox": [100, 150, 300, 350]}
    ],
    "motif_count": 1,
}

def test_retorna_imagen_reconstruida():
    """Debe retornar una ruta de imagen reconstruida (puede ser la original)."""
    result = reconstructor_node(MOCK_STATE_FOR_RECON)
    assert "reconstructed_image" in result
    assert result["reconstructed_image"] is not None

def test_retorna_flag_reconstruction_applied():
    """Debe indicar si se aplicó reconstrucción GAN o no."""
    result = reconstructor_node(MOCK_STATE_FOR_RECON)
    assert "reconstruction_applied" in result
    assert isinstance(result["reconstruction_applied"], bool)

def test_sin_modelo_gan_no_rompe_pipeline():
    """Sin pesos GAN disponibles, debe retornar imagen original sin error."""
    result = reconstructor_node(MOCK_STATE_FOR_RECON)
    # Si el placeholder está activo, reconstruction_applied=False
    if not result["reconstruction_applied"]:
        assert result["reconstructed_image"] == MOCK_STATE_FOR_RECON["enhanced_image"]
