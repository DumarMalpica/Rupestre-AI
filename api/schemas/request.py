"""Schemas de entrada de la API."""

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    site_name: str = Field(..., description="Nombre del sitio rupestre")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    notes: str = Field(default="", description="Notas del arqueólogo")
