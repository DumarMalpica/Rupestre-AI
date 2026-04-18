"""AG2 — Motif Detector | Dev 1"""

import logging
from core.state import RupestreState
from core.logger import get_tracer, get_logger
from core.exceptions import AgentExecutionError

logger = get_logger("motif_detector")


def motif_detector_node(state: RupestreState) -> dict:
    """
    Nodo 2 del grafo. Detecta motivos rupestres en la imagen realzada.

    Lee:   enhanced_image
    Escribe: detected_motifs, motif_count
    """
    tracer = get_tracer()
    enhanced_image = state["enhanced_image"]
    logger.info(f"Detectando motivos en: {enhanced_image}")

    with tracer.trace(name="motif_detector"):
        try:
            # TODO: implementar tools/yolo_detector.py y tools/sam_segmenter.py
            # motifs = yolo_detector.detect(enhanced_image)
            # motifs = sam_segmenter.segment(motifs, enhanced_image)

            # ── PLACEHOLDER ───────────────────────────────────
            detected_motifs = [
                {
                    "id": "motif_001",
                    "clase": "espiral",
                    "confidence": 0.91,
                    "bbox": [100, 150, 300, 350],
                    "crop_path": None,
                    "mask": None,
                }
            ]
            motif_count = len(detected_motifs)
            # ─────────────────────────────────────────────────

            logger.info(f"{motif_count} motivo(s) detectado(s)")

            return {
                "detected_motifs": detected_motifs,
                "motif_count": motif_count,
                "current_agent": "motif_detector",
            }

        except Exception as e:
            logger.error(f"Error en motif_detector: {e}")
            raise AgentExecutionError("motif_detector", str(e))
