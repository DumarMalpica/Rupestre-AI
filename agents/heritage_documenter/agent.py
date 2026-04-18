"""AG6 — Heritage Documenter | Dev 2"""

import uuid
from datetime import datetime
from core.state import RupestreState
from core.logger import get_tracer, get_logger
from core.exceptions import DocumentationError

logger = get_logger("heritage_documenter")


def documenter_node(state: RupestreState) -> dict:
    """
    Nodo 6 del grafo — último. Genera la ficha oficial ICANH en PDF y JSON.

    Lee:   todo el estado previo
    Escribe: ficha_pdf_path, ficha_json, record_id
    """
    tracer = get_tracer()
    site = state.get("site_name", "desconocido")
    record_id = str(uuid.uuid4())[:8].upper()

    logger.info(f"Generando ficha ICANH para: {site} | ID: {record_id}")

    with tracer.trace(name="heritage_documenter", metadata={"site": site}):
        try:
            # TODO: implementar tools/json_builder.py, tools/pdf_generator.py
            # ficha_json = json_builder.build(state)
            # pdf_path = pdf_generator.render(ficha_json)

            # ── PLACEHOLDER ───────────────────────────────────
            ficha_json = {
                "record_id": record_id,
                "generated_at": datetime.utcnow().isoformat(),
                "site_name": site,
                "coordinates": state.get("coordinates"),
                "motif_count": state.get("motif_count", 0),
                "has_regional_parallels": state.get("has_regional_parallels", False),
                "cultural_interpretation": state.get("cultural_interpretation"),
                "cited_sources": state.get("cited_sources", []),
                "reconstruction_applied": state.get("reconstruction_applied", False),
                "images": {
                    "original": state.get("image_path"),
                    "enhanced": state.get("enhanced_image"),
                    "reconstructed": state.get("reconstructed_image"),
                },
            }
            pdf_path = f"./data/fichas/{record_id}_ficha_icanh.pdf"
            # ─────────────────────────────────────────────────

            logger.info(f"Ficha generada — ID: {record_id}")

            return {
                "ficha_pdf_path": pdf_path,
                "ficha_json": ficha_json,
                "record_id": record_id,
                "current_agent": "heritage_documenter",
            }

        except Exception as e:
            logger.error(f"Error en heritage_documenter: {e}")
            raise DocumentationError(str(e))
