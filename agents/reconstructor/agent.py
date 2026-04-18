"""AG5 — Reconstructor | Dev 1"""

from core.state import RupestreState
from core.logger import get_tracer, get_logger
from core.exceptions import AgentExecutionError

logger = get_logger("reconstructor")

DETERIORATION_THRESHOLD = 0.3  # % mínimo de deterioro para aplicar GAN


def reconstructor_node(state: RupestreState) -> dict:
    """
    Nodo 5 del grafo. Reconstruye zonas deterioradas con DeepFillv2.

    Lee:   enhanced_image, detected_motifs
    Escribe: reconstructed_image, confidence_map, reconstruction_applied
    """
    tracer = get_tracer()
    image = state.get("enhanced_image", "")
    logger.info(f"Evaluando reconstrucción GAN para: {image}")

    with tracer.trace(name="reconstructor"):
        try:
            # TODO: implementar tools/mask_generator.py y tools/inpainter.py
            # mask = mask_generator.detect_deterioration(image)
            # if mask.deterioration_ratio > DETERIORATION_THRESHOLD:
            #     result = inpainter.inpaint(image, mask)
            #     confidence = confidence.generate_map(result)

            # ── PLACEHOLDER ───────────────────────────────────
            reconstruction_applied = False   # sin GAN entrenado aún
            reconstructed_image = image      # imagen original sin cambios
            confidence_map = None
            # ─────────────────────────────────────────────────

            logger.info(f"Reconstrucción aplicada: {reconstruction_applied}")

            return {
                "reconstructed_image": reconstructed_image,
                "confidence_map": confidence_map,
                "reconstruction_applied": reconstruction_applied,
                "current_agent": "reconstructor",
            }

        except Exception as e:
            logger.error(f"Error en reconstructor: {e}")
            raise AgentExecutionError("reconstructor", str(e))
