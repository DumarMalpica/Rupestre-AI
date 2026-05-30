from __future__ import annotations

import pytest

from agents.motif_detector.agent import motif_detector_node
from core.state import RupestreState


def _make_state(image_path: str = "") -> RupestreState:
    return RupestreState(
        image_path=image_path,
        enhanced_image=image_path,
        session_id="pytest-ag2",
        errors=[],
        current_agent="image_processor",
    )


def test_returns_list():
    result = motif_detector_node(_make_state())
    assert isinstance(result["detected_motifs"], list)


def test_count_matches_list():
    result = motif_detector_node(_make_state())
    assert result["motif_count"] == len(result["detected_motifs"])


def test_motif_has_required_fields():
    result = motif_detector_node(_make_state())
    for motif in result["detected_motifs"]:
        assert "id" in motif
        assert "clase" in motif
        assert "confidence" in motif
        assert "bbox" in motif


def test_confidence_range():
    result = motif_detector_node(_make_state())
    for motif in result["detected_motifs"]:
        assert 0.0 <= motif["confidence"] <= 1.0


def test_no_crash_without_image():
    result = motif_detector_node(_make_state(image_path=""))
    assert "detected_motifs" in result
