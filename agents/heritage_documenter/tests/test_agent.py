from __future__ import annotations

from pathlib import Path

import pytest

from agents.heritage_documenter.agent import heritage_documenter_node
from core.state import RupestreState

_REQUIRED_FIELDS = {
    "record_id",
    "generated_at",
    "site_name",
    "coordinates",
    "department",
    "municipality",
    "motif_count",
    "detected_motifs",
    "similar_motifs",
    "has_regional_parallels",
    "cultural_interpretation",
    "cited_sources",
    "interpretation_confidence",
    "reconstruction_applied",
    "images",
}


@pytest.fixture(autouse=True)
def mock_pdf(monkeypatch, tmp_path):
    """Evita la dependencia de sistema de WeasyPrint en tests."""

    def _fake_pdf(html_content: str, output_path: str) -> str:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(b"%PDF-1.4 fake")
        return output_path

    monkeypatch.setattr(
        "agents.heritage_documenter.agent.generate_pdf", _fake_pdf
    )
    import core.config as cfg

    monkeypatch.setattr(cfg.settings, "output_dir", str(tmp_path))


def _make_state() -> RupestreState:
    return RupestreState(
        image_path="data/samples/pictograma.jpg",
        enhanced_image="data/fichas/pictograma_enhanced.jpg",
        reconstructed_image="",
        site_name="Cerro Pintado — Boyacá",
        coordinates=(5.5353, -73.6241),
        motif_count=2,
        detected_motifs=[
            {
                "id": "motif_001",
                "clase": "espiral",
                "confidence": 0.91,
                "bbox": [120, 80, 340, 290],
                "crop_path": None,
                "mask": None,
            },
        ],
        similar_motifs=[
            {
                "motif_id": "motif_001",
                "top_matches": [
                    {
                        "site": "Villa de Leyva",
                        "score": 0.88,
                        "cultura": "Muisca",
                        "periodo": "600-1600 d.C.",
                    }
                ],
            }
        ],
        has_regional_parallels=True,
        cultural_interpretation=(
            "Los motivos en espiral presentan características "
            "del período Muisca tardío."
        ),
        cited_sources=[
            {
                "title": "Por las tramas de Sutatausa",
                "author": "Londoño, W.",
                "year": "2003",
            }
        ],
        interpretation_confidence=0.82,
        requires_human_review=False,
        reconstruction_applied=False,
        session_id="pytest-ag6",
        errors=[],
        current_agent="reconstructor",
    )


def test_record_id_not_empty():
    result = heritage_documenter_node(_make_state())
    assert isinstance(result["record_id"], str)
    assert len(result["record_id"]) > 0


def test_different_record_ids():
    result_a = heritage_documenter_node(_make_state())
    result_b = heritage_documenter_node(_make_state())
    assert result_a["record_id"] != result_b["record_id"]


def test_ficha_json_has_required_fields():
    result = heritage_documenter_node(_make_state())
    ficha = result["ficha_json"]
    missing = _REQUIRED_FIELDS - ficha.keys()
    assert not missing, f"Campos ausentes en ficha: {missing}"


def test_site_name_in_ficha():
    state = _make_state()
    result = heritage_documenter_node(state)
    assert result["ficha_json"]["site_name"] == state["site_name"]


def test_pdf_path_string():
    result = heritage_documenter_node(_make_state())
    assert isinstance(result["ficha_pdf_path"], str)
    assert len(result["ficha_pdf_path"]) > 0
