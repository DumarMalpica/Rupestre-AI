"""Schemas de respuesta de la API."""

from typing import Optional
from pydantic import BaseModel


class AnalysisResponse(BaseModel):
    session_id: str
    status: str  # pending | processing | done | error
    record_id: Optional[str] = None
    message: str = ""


class RecordResponse(BaseModel):
    record_id: str
    site_name: str
    motif_count: int
    has_regional_parallels: bool
    cultural_interpretation: Optional[str]
    reconstruction_applied: bool
    ficha_pdf_url: Optional[str]
