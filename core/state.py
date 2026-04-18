"""
Estado compartido entre todos los agentes del grafo LangGraph.

CONTRATO: Cada campo indica qué agente lo ESCRIBE y quién lo LEE.
Modificar este archivo requiere consenso de ambos desarrolladores.
"""

from typing import Any, Optional
from typing_extensions import TypedDict


class RupestreState(TypedDict):
    # ── INPUT (usuario / bot / API) ───────────────────────────
    image_path: str  # ruta imagen original subida
    site_name: str  # nombre del sitio rupestre
    coordinates: tuple[float, float]  # (lat, lon) del sitio
    session_id: str  # ID único de la sesión

    # ── AG1: Image Processor ─────────────────────────────────
    # Escribe: AG1 | Lee: AG2, AG5
    enhanced_image: Optional[str]  # ruta imagen realzada
    image_quality_ok: Optional[bool]  # False = detener el grafo

    # ── AG2: Motif Detector ───────────────────────────────────
    # Escribe: AG2 | Lee: AG3, AG5, AG6
    detected_motifs: Optional[list[dict[str, Any]]]
    motif_count: Optional[int]

    # ── AG3: Iconographic Comparator ─────────────────────────
    # Escribe: AG3 | Lee: AG4, AG6
    similar_motifs: Optional[list[dict[str, Any]]]
    has_regional_parallels: Optional[bool]

    # ── AG4: Cultural Analyst ────────────────────────────────
    # Escribe: AG4 | Lee: AG6
    cultural_interpretation: Optional[str]
    cited_sources: Optional[list[dict[str, Any]]]
    interpretation_confidence: Optional[float]
    requires_human_review: Optional[bool]  # HITL flag

    # ── AG5: Reconstructor ───────────────────────────────────
    # Escribe: AG5 | Lee: AG6
    reconstructed_image: Optional[str]
    confidence_map: Optional[str]
    reconstruction_applied: Optional[bool]

    # ── AG6: Heritage Documenter ─────────────────────────────
    # Escribe: AG6 | Lee: API, Bot
    ficha_pdf_path: Optional[str]
    ficha_json: Optional[dict[str, Any]]
    record_id: Optional[str]

    # ── CONTROL ───────────────────────────────────────────────
    errors: Optional[list[str]]  # errores acumulados por agentes
    current_agent: Optional[str]  # agente ejecutando actualmente
