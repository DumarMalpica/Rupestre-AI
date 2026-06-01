from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from agents.image_processor.agent import image_processor_node
from core.state import RupestreState


@pytest.fixture()
def valid_image(tmp_path) -> str:
    """Imagen RGB 1200x900 (1.08 MP) con textura suficiente para superar blur."""
    img_array = np.zeros((900, 1200, 3), dtype=np.uint8)
    # Patrón de tablero de ajedrez → varianza de Laplaciano alta (no borrosa)
    for i in range(900):
        for j in range(1200):
            if (i // 20 + j // 20) % 2 == 0:
                img_array[i, j] = [180, 60, 60]
            else:
                img_array[i, j] = [60, 60, 180]

    path = tmp_path / "test_rupestre.jpg"
    Image.fromarray(img_array, "RGB").save(str(path))
    return str(path)


@pytest.fixture()
def small_image(tmp_path) -> str:
    """Imagen 10x10 → muy por debajo de 1 MP."""
    img = Image.new("RGB", (10, 10), color=(200, 100, 50))
    path = tmp_path / "small.jpg"
    img.save(str(path))
    return str(path)


def _make_state(image_path: str) -> RupestreState:
    return RupestreState(
        image_path=image_path,
        site_name="Sitio Test",
        coordinates=(4.71, -74.07),
        session_id="pytest-session",
        errors=[],
        current_agent="",
    )


def test_valid_image_passes_quality(valid_image, tmp_path, monkeypatch):
    import core.config as cfg

    monkeypatch.setattr(cfg.settings, "output_dir", str(tmp_path))
    result = image_processor_node(_make_state(valid_image))
    assert result["image_quality_ok"] is True


def test_enhanced_image_not_none(valid_image, tmp_path, monkeypatch):
    import core.config as cfg

    monkeypatch.setattr(cfg.settings, "output_dir", str(tmp_path))
    result = image_processor_node(_make_state(valid_image))
    enhanced = result.get("enhanced_image")
    assert enhanced is not None
    assert enhanced != ""


def test_no_foreign_fields(valid_image, tmp_path, monkeypatch):
    import core.config as cfg

    monkeypatch.setattr(cfg.settings, "output_dir", str(tmp_path))
    result = image_processor_node(_make_state(valid_image))
    assert "detected_motifs" not in result
    assert "motif_count" not in result


def test_missing_file_no_crash():
    result = image_processor_node(_make_state("no_existe.jpg"))
    assert result["image_quality_ok"] is False
    assert len(result["errors"]) > 0


def test_small_image_fails(small_image, tmp_path, monkeypatch):
    import core.config as cfg

    monkeypatch.setattr(cfg.settings, "output_dir", str(tmp_path))
    result = image_processor_node(_make_state(small_image))
    assert result["image_quality_ok"] is False
