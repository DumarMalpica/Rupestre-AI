from agents.reconstructor.tools.lama_inpainter import inpaint_with_lama
from agents.reconstructor.tools.mask_generator import generate_mask
from core.exceptions import AgentExecutionError
from core.logger import get_logger, langfuse_context, observe
from core.state import RupestreState

logger = get_logger("lama_enhancer")


@observe(name="lama_inpainting")
def _lama_span(image_path: str, mask_path: str | None) -> tuple[str, bool]:
    result_path, applied = inpaint_with_lama(image_path, mask_path)
    langfuse_context.update_current_observation(
        output={"lama_applied": applied}
    )
    return result_path, applied


@observe(name="lama_enhancer")
def lama_enhancer_node(state: RupestreState) -> dict:
    langfuse_context.update_current_trace(
        session_id=state.get("session_id", "default"),
        input={
            "input_image": state.get("reconstructed_image"),
            "mask_generated_from": state.get("enhanced_image"),
        },
        tags=["rupestre-ai", "lama"],
    )

    try:
        input_image = state.get("reconstructed_image") or state["enhanced_image"]
        mask_path = generate_mask(state["enhanced_image"])
        reconstructed, applied = _lama_span(input_image, mask_path)

        logger.info(f"LaMa enhancement: mask={mask_path is not None} applied={applied}")
        result = {
            "lama_reconstructed_image": reconstructed,
            "lama_reconstruction_applied": applied,
            "reconstructed_image": reconstructed if applied else state.get("reconstructed_image"),
            "current_agent": "lama_enhancer",
        }
        langfuse_context.update_current_trace(
            output={
                "lama_applied": applied,
                "lama_output": reconstructed,
            }
        )
        return result

    except Exception as exc:
        logger.error(f"Error en lama_enhancer_node: {exc}")
        langfuse_context.update_current_trace(
            output={"error": str(exc)}, level="ERROR"
        )
        raise AgentExecutionError("lama_enhancer", str(exc)) from exc
