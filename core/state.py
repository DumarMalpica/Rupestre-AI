from __future__ import annotations

from typing import TypedDict


class RupestreState(TypedDict, total=False):
    # INPUT usuario
    image_path: str
    site_name: str
    coordinates: tuple[float, float]
    session_id: str
    # AG1
    enhanced_image: str
    image_quality_ok: bool
    # AG2
    detected_motifs: list[dict]
    motif_count: int
    # AG3
    similar_motifs: list[dict]
    has_regional_parallels: bool
    # AG4
    cultural_interpretation: str
    cited_sources: list[dict]
    interpretation_confidence: float
    requires_human_review: bool
    # AG5
    reconstructed_image: str
    confidence_map: str | None
    reconstruction_applied: bool
    # LaMa (paso extra después de AG5)
    lama_reconstructed_image: str
    lama_reconstruction_applied: bool
    # AG6
    ficha_pdf_path: str
    ficha_json: dict
    record_id: str
    # Control
    errors: list[str]
    current_agent: str
