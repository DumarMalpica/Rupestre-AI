from __future__ import annotations

from core.exceptions import AgentExecutionError
from core.logger import get_logger
from core.state import RupestreState

from agents.reconstructor.tools.confidence import generate_confidence_map
from agents.reconstructor.tools.inpainter import inpaint_image
from agents.reconstructor.tools.mask_generator import generate_mask

logger = get_logger("reconstructor")


def reconstructor_node(state: RupestreState) -> dict:
    enhanced_image = state.get("enhanced_image", state.get("image_path", ""))

    try:
        mask_path = generate_mask(enhanced_image)
        reconstructed_image, applied = inpaint_image(enhanced_image, mask_path)
        confidence_map = (
            generate_confidence_map(enhanced_image, reconstructed_image)
            if applied
            else None
        )

        logger.info(
            "Reconstrucción: mask=%s applied=%s", mask_path is not None, applied
        )

        return {
            "reconstructed_image": reconstructed_image,
            "confidence_map": confidence_map,
            "reconstruction_applied": applied,
            "current_agent": "reconstructor",
        }

    except Exception as exc:
        logger.exception("Error en reconstructor_node")
        raise AgentExecutionError("reconstructor", str(exc)) from exc
