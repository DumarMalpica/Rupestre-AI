"""AG1 — Image Processor | Dev 1"""

import logging
from core.state import RupestreState
from core.logger import get_tracer, get_logger
from core.exceptions import ImageQualityError

logger = get_logger("image_processor")


def image_processor_node(state: RupestreState) -> dict:
    """
    Nodo 1 del grafo. Realza la imagen y evalúa su calidad.

    Lee:   image_path, site_name, coordinates
    Escribe: enhanced_image, image_quality_ok
    """
    tracer = get_tracer()
    image_path = state["image_path"]
    logger.info(f"Procesando imagen: {image_path}")

    with tracer.trace(
        name="image_processor", metadata={"site": state.get("site_name")}
    ):
        try:
            # TODO: implementar tools/enhancer.py y tools/quality.py
            # enhanced = enhancer.apply_dstretch(image_path)
            # quality_ok = quality.evaluate(enhanced)

            # ── PLACEHOLDER ───────────────────────────────────
            enhanced_image = image_path  # sin procesamiento aún
            image_quality_ok = True  # siempre válida por ahora
            # ─────────────────────────────────────────────────

            logger.info(f"Imagen procesada. Calidad OK: {image_quality_ok}")

            return {
                "enhanced_image": enhanced_image,
                "image_quality_ok": image_quality_ok,
                "current_agent": "image_processor",
            }

        except Exception as e:
            logger.error(f"Error en image_processor: {e}")
            return {
                "image_quality_ok": False,
                "errors": state.get("errors", []) + [str(e)],
            }
