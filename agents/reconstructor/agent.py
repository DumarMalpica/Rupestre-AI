from core.logger import get_logger, langfuse_context, observe
from core.exceptions import AgentExecutionError
from core.state import RupestreState
from agents.reconstructor.tools.mask_generator import generate_mask
from agents.reconstructor.tools.inpainter import inpaint_image
from agents.reconstructor.tools.confidence import generate_confidence_map

logger = get_logger("reconstructor")


@observe(name="mask_generation")
def _mask_span(enhanced: str) -> str | None:
    mask_path = generate_mask(enhanced)
    langfuse_context.update_current_observation(
        output={"mask_generated": mask_path is not None}
    )
    return mask_path


@observe(name="inpainting")
def _inpaint_span(enhanced: str, mask_path: str | None) -> tuple[str, bool]:
    reconstructed, applied = inpaint_image(enhanced, mask_path)
    langfuse_context.update_current_observation(output={"applied": applied})
    return reconstructed, applied


@observe(name="ag5_reconstructor")
def reconstructor_node(state: RupestreState) -> dict:
    langfuse_context.update_current_trace(
        session_id=state.get("session_id", "default"),
        input={"enhanced_image": state.get("enhanced_image"),
               "motif_count": state.get("motif_count", 0)},
        tags=["rupestre-ai", "ag5"],
    )

    try:
        enhanced = state["enhanced_image"]

        mask_path = _mask_span(enhanced)
        reconstructed, applied = _inpaint_span(enhanced, mask_path)
        confidence_map = (
            generate_confidence_map(enhanced, reconstructed) if applied else None
        )

        logger.info(f"Reconstrucción: mask={mask_path is not None} applied={applied}")
        result = {"reconstructed_image": reconstructed,
                  "confidence_map": confidence_map,
                  "reconstruction_applied": applied,
                  "current_agent": "reconstructor"}
        langfuse_context.update_current_trace(
            output={"reconstruction_applied": applied}
        )
        return result

    except Exception as exc:
        logger.error(f"Error en reconstructor_node: {exc}")
        langfuse_context.update_current_trace(
            output={"error": str(exc)}, level="ERROR"
        )
        raise AgentExecutionError("reconstructor", str(exc)) from exc
