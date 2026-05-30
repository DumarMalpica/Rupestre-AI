from __future__ import annotations

from core.config import settings
from core.exceptions import AgentExecutionError
from core.logger import get_logger
from core.state import RupestreState

from agents.motif_detector.tools.annotator import annotate_image
from agents.motif_detector.tools.sam_segmenter import segment_motifs
from agents.motif_detector.tools.yolo_detector import detect_motifs

logger = get_logger("motif_detector")


def motif_detector_node(state: RupestreState) -> dict:
    enhanced_image = state.get("enhanced_image", state.get("image_path", ""))

    try:
        motifs = detect_motifs(enhanced_image)
        motifs = segment_motifs(enhanced_image, motifs)
        annotate_image(enhanced_image, motifs, settings.output_dir)

        logger.info("Detectados %d motivos en %s", len(motifs), enhanced_image)

        return {
            "detected_motifs": motifs,
            "motif_count": len(motifs),
            "current_agent": "motif_detector",
        }

    except Exception as exc:
        logger.exception("Error en motif_detector_node")
        raise AgentExecutionError("motif_detector", str(exc)) from exc
