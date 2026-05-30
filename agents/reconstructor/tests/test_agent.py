from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from agents.reconstructor.agent import reconstructor_node
from core.state import RupestreState


@pytest.fixture()
def textured_image(tmp_path) -> str:
    """Imagen de alta frecuencia (tablero 1px): Laplaciano elevado en toda la imagen
    → varianza local > 20 en casi todos los píxeles → máscara < 1% → None."""
    arr = np.zeros((200, 200, 3), dtype=np.uint8)
    for i in range(200):
        for j in range(200):
            arr[i, j] = 255 if (i + j) % 2 == 0 else 0
    path = tmp_path / "textured.png"  # PNG: sin pérdida por compresión JPEG
    Image.fromarray(arr).save(str(path))
    return str(path)


def _make_state(image_path: str = "") -> RupestreState:
    return RupestreState(
        image_path=image_path,
        enhanced_image=image_path,
        session_id="pytest-ag5",
        errors=[],
        current_agent="cultural_analyst",
    )


def test_reconstructed_not_none():
    result = reconstructor_node(_make_state("imagen_inexistente.jpg"))
    assert result["reconstructed_image"] is not None


def test_applied_is_bool():
    result = reconstructor_node(_make_state("imagen_inexistente.jpg"))
    assert isinstance(result["reconstruction_applied"], bool)


def test_no_gan_no_crash():
    # Sin pesos GAN el mock retorna la imagen original sin lanzar excepción
    result = reconstructor_node(_make_state("imagen_inexistente.jpg"))
    assert "reconstructed_image" in result


def test_no_deterioration_applied_false(textured_image, tmp_path, monkeypatch):
    import core.config as cfg

    monkeypatch.setattr(cfg.settings, "output_dir", str(tmp_path))
    result = reconstructor_node(_make_state(textured_image))
    assert result["reconstruction_applied"] is False
