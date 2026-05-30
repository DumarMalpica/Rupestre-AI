from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    site_name: str = Field(..., description="Nombre del sitio arqueológico")
    latitude: float = Field(..., description="Latitud decimal (WGS84)")
    longitude: float = Field(..., description="Longitud decimal (WGS84)")
