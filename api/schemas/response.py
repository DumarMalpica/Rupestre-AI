from __future__ import annotations

from pydantic import BaseModel


class AnalyzeResponse(BaseModel):
    record_id: str
    motif_count: int
    cultural_interpretation: str
    interpretation_confidence: float
    reconstruction_applied: bool
    pdf_available: bool
    requires_human_review: bool
    processing_time_seconds: float


class RecordResponse(BaseModel):
    # Campos de FichaICANH
    record_id: str
    generated_at: str
    site_name: str
    coordinates: tuple[float, float]
    department: str
    municipality: str
    motif_count: int
    detected_motifs: list[dict]
    similar_motifs: list[dict]
    has_regional_parallels: bool
    cultural_interpretation: str
    cited_sources: list[dict]
    interpretation_confidence: float
    reconstruction_applied: bool
    requires_human_review: bool
    images: dict
    # Campo adicional de la API
    pdf_available: bool
