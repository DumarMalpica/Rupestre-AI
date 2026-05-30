from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from core.state import RupestreState


class FichaICANH(BaseModel):
    record_id: str
    generated_at: str
    site_name: str
    coordinates: tuple[float, float]
    department: str = "No especificado"
    municipality: str = "No especificado"
    motif_count: int
    detected_motifs: list[dict]
    similar_motifs: list[dict]
    has_regional_parallels: bool
    cultural_interpretation: str
    cited_sources: list[dict]
    interpretation_confidence: float
    reconstruction_applied: bool
    requires_human_review: bool = False
    images: dict


def build_ficha_json(state: RupestreState, record_id: str) -> dict:
    ficha = FichaICANH(
        record_id=record_id,
        generated_at=datetime.now().isoformat(),
        site_name=state.get("site_name", "Sitio desconocido"),
        coordinates=state.get("coordinates", (0.0, 0.0)),
        motif_count=state.get("motif_count", 0),
        detected_motifs=state.get("detected_motifs", []),
        similar_motifs=state.get("similar_motifs", []),
        has_regional_parallels=state.get("has_regional_parallels", False),
        cultural_interpretation=state.get("cultural_interpretation", ""),
        cited_sources=state.get("cited_sources", []),
        interpretation_confidence=state.get("interpretation_confidence", 0.0),
        reconstruction_applied=state.get("reconstruction_applied", False),
        requires_human_review=state.get("requires_human_review", False),
        images={
            "original": state.get("image_path", ""),
            "enhanced": state.get("enhanced_image", ""),
            "reconstructed": state.get("reconstructed_image", "") or "",
        },
    )
    return ficha.model_dump()
