from core.logger import get_logger, langfuse_context, observe
from core.config import settings
from core.exceptions import AgentExecutionError
from core.state import RupestreState
from agents.image_processor.tools.quality import check_quality
from agents.image_processor.tools.enhancer import enhance_image

logger = get_logger("image_processor")


@observe(name="quality_check")
def _quality_span(image_path: str) -> tuple[bool, str]:
    passed, reason = check_quality(image_path)
    langfuse_context.update_current_observation(
        output={"passed": passed, "reason": reason}
    )
    return passed, reason


@observe(name="enhance_image")
def _enhance_span(image_path: str, output_dir: str) -> str:
    enhanced = enhance_image(image_path, output_dir)
    langfuse_context.update_current_observation(
        output={"enhanced_path": enhanced}
    )
    return enhanced


@observe(name="ag1_image_processor")
def image_processor_node(state: RupestreState) -> dict:
    langfuse_context.update_current_trace(
        session_id=state.get("session_id", "default"),
        input={"image_path": state.get("image_path"),
               "site_name": state.get("site_name")},
        tags=["rupestre-ai", "ag1"],
    )

    errors = list(state.get("errors", []))

    try:
        image_path = state["image_path"]

        passed, reason = _quality_span(image_path)

        if not passed:
            logger.warning(f"Calidad rechazada: {reason}")
            errors.append(reason)
            result = {"image_quality_ok": False, "enhanced_image": image_path,
                      "errors": errors, "current_agent": "image_processor"}
            langfuse_context.update_current_trace(output=result, level="WARNING")
            return result

        enhanced = _enhance_span(image_path, settings.output_dir)
        logger.info(f"Imagen realzada → {enhanced}")
        result = {"image_quality_ok": True, "enhanced_image": enhanced,
                  "errors": errors, "current_agent": "image_processor"}
        langfuse_context.update_current_trace(output=result)
        return result

    except Exception as exc:
        logger.error(f"Error en image_processor_node: {exc}")
        langfuse_context.update_current_trace(
            output={"error": str(exc)}, level="ERROR"
        )
        raise AgentExecutionError("image_processor", str(exc)) from exc
