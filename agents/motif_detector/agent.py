from agents.motif_detector.tools.annotator import annotate_image
from agents.motif_detector.tools.sam_segmenter import segment_motifs
from agents.motif_detector.tools.yolo_detector import detect_motifs
from core.config import settings
from core.exceptions import AgentExecutionError
from core.logger import get_logger, langfuse_context, observe
from core.state import RupestreState

logger = get_logger("motif_detector")


@observe(name="yolo_detection")
def _yolo_span(image: str) -> list[dict]:
    motifs = detect_motifs(image)
    langfuse_context.update_current_observation(
        output={"motif_count": len(motifs)}
    )
    return motifs


@observe(name="sam_segmentation")
def _sam_span(image: str, motifs: list[dict]) -> list[dict]:
    segmented = segment_motifs(image, motifs)
    langfuse_context.update_current_observation(
        output={"segmented": len(segmented)}
    )
    return segmented


@observe(name="annotation")
def _annotation_span(image: str, motifs: list[dict], output_dir: str) -> None:
    annotate_image(image, motifs, output_dir)
    langfuse_context.update_current_observation(output={"done": True})


@observe(name="ag2_motif_detector")
def motif_detector_node(state: RupestreState) -> dict:
    langfuse_context.update_current_trace(
        session_id=state.get("session_id", "default"),
        input={"enhanced_image": state.get("enhanced_image")},
        tags=["rupestre-ai", "ag2"],
    )

    try:
        enhanced = state["enhanced_image"]

        motifs = _yolo_span(enhanced)
        motifs = _sam_span(enhanced, motifs)
        _annotation_span(enhanced, motifs, settings.output_dir)

        logger.info(f"Detectados {len(motifs)} motivos en {enhanced}")
        result = {"detected_motifs": motifs,
                  "motif_count": len(motifs),
                  "current_agent": "motif_detector"}
        langfuse_context.update_current_trace(
            output={"motif_count": len(motifs),
                    "clases": [m["clase"] for m in motifs]}
        )
        return result

    except Exception as exc:
        logger.error(f"Error en motif_detector_node: {exc}")
        langfuse_context.update_current_trace(
            output={"error": str(exc)}, level="ERROR"
        )
        raise AgentExecutionError("motif_detector", str(exc)) from exc
