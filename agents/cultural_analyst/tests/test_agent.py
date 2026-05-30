from __future__ import annotations

import pytest

from agents.cultural_analyst.agent import cultural_analyst_node
from core.state import RupestreState

_MOTIFS = [
    {"id": "motif_001", "clase": "espiral", "confidence": 0.91,
     "bbox": [120, 80, 340, 290], "crop_path": None, "mask": None},
]
_SIMILAR = [
    {"motif_id": "motif_001", "top_matches": [
        {"site": "Villa de Leyva", "score": 0.88, "cultura": "Muisca", "periodo": "600-1600 d.C."}
    ]},
]


def _make_state() -> RupestreState:
    return RupestreState(
        image_path="fake.jpg",
        enhanced_image="fake.jpg",
        site_name="Sitio Rupestre Test",
        coordinates=(5.53, -73.62),
        detected_motifs=_MOTIFS,
        similar_motifs=_SIMILAR,
        session_id="pytest-ag4",
        errors=[],
        current_agent="iconographic_comparator",
    )


def test_interpretation_not_empty():
    result = cultural_analyst_node(_make_state())
    assert len(result["cultural_interpretation"]) > 10


def test_sources_is_list():
    result = cultural_analyst_node(_make_state())
    assert isinstance(result["cited_sources"], list)


def test_confidence_range():
    result = cultural_analyst_node(_make_state())
    conf = result["interpretation_confidence"]
    assert 0.0 <= conf <= 1.0


def test_hitl_flag_present():
    result = cultural_analyst_node(_make_state())
    assert isinstance(result["requires_human_review"], bool)


def test_mock_no_external_calls(monkeypatch):
    import core.config as cfg

    monkeypatch.setattr(cfg.settings, "llm_provider", "mock")

    def _assert_not_called(*args, **kwargs):
        pytest.fail("requests.post fue invocado en modo mock")

    try:
        import requests
        monkeypatch.setattr(requests, "post", _assert_not_called)
    except ImportError:
        pass  # requests no instalado → imposible llamar HTTP

    result = cultural_analyst_node(_make_state())
    assert len(result["cultural_interpretation"]) > 10
