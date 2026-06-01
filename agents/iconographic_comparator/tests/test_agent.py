from __future__ import annotations

from agents.iconographic_comparator.agent import iconographic_comparator_node
from core.state import RupestreState

_MOCK_MOTIFS = [
    {
        "id": "motif_001",
        "clase": "espiral",
        "confidence": 0.91,
        "bbox": [120, 80, 340, 290],
        "crop_path": None,
        "mask": None,
    },
    {
        "id": "motif_002",
        "clase": "figura_antropomorfa",
        "confidence": 0.78,
        "bbox": [400, 150, 580, 380],
        "crop_path": None,
        "mask": None,
    },
]


def _make_state(detected_motifs: list[dict] | None = None) -> RupestreState:
    return RupestreState(
        image_path="fake.jpg",
        enhanced_image="fake.jpg",
        detected_motifs=detected_motifs if detected_motifs is not None else _MOCK_MOTIFS,
        motif_count=len(detected_motifs) if detected_motifs is not None else len(_MOCK_MOTIFS),
        session_id="pytest-ag3",
        errors=[],
        current_agent="motif_detector",
    )


def test_returns_list():
    result = iconographic_comparator_node(_make_state())
    assert isinstance(result["similar_motifs"], list)


def test_parallels_is_bool():
    result = iconographic_comparator_node(_make_state())
    assert isinstance(result["has_regional_parallels"], bool)


def test_scores_in_range():
    result = iconographic_comparator_node(_make_state())
    for entry in result["similar_motifs"]:
        for match in entry["top_matches"]:
            assert 0.0 <= match["score"] <= 1.0


def test_empty_motifs_no_crash():
    result = iconographic_comparator_node(_make_state(detected_motifs=[]))
    assert result["similar_motifs"] == []
    assert result["has_regional_parallels"] is False
