from __future__ import annotations

from core.config import settings
from core.exceptions import AgentExecutionError
from core.logger import get_logger
from core.state import RupestreState

from agents.image_processor.tools.enhancer import enhance_image
from agents.image_processor.tools.quality import check_quality

logger = get_logger("image_processor")


def image_processor_node(state: RupestreState) -> dict:
    image_path = state.get("image_path", "")
    errors = list(state.get("errors", []))

    try:
        ok, reason = check_quality(image_path)

        if not ok:
            logger.warning("Calidad de imagen rechazada: %s", reason)
            return {
                "image_quality_ok": False,
                "enhanced_image": image_path,
                "errors": errors + [reason],
                "current_agent": "image_processor",
            }

        enhanced_path = enhance_image(image_path, settings.output_dir)
        logger.info("Imagen realzada → %s", enhanced_path)

        return {
            "image_quality_ok": True,
            "enhanced_image": enhanced_path,
            "errors": errors,
            "current_agent": "image_processor",
        }

    except Exception as exc:
        msg = str(exc)
        logger.exception("Error en image_processor_node")
        raise AgentExecutionError("image_processor", msg) from exc
