from __future__ import annotations

from core.exceptions import AgentExecutionError
from core.logger import get_logger
from core.state import RupestreState

from agents.iconographic_comparator.tools.retriever import retrieve_similar
from agents.iconographic_comparator.tools.scorer import score_matches

logger = get_logger("iconographic_comparator")


def iconographic_comparator_node(state: RupestreState) -> dict:
    detected_motifs: list[dict] = state.get("detected_motifs", [])

    try:
        similar_motifs: list[dict] = []
        for motif in detected_motifs:
            matches = retrieve_similar(motif)
            matches = score_matches(matches)
            similar_motifs.append(
                {"motif_id": motif["id"], "top_matches": matches}
            )

        has_regional_parallels = any(
            match["score"] > 0.75
            for result in similar_motifs
            for match in result["top_matches"]
        )

        logger.info(
            "Comparación iconográfica: %d motivos, paralelos=%s",
            len(similar_motifs),
            has_regional_parallels,
        )

        return {
            "similar_motifs": similar_motifs,
            "has_regional_parallels": has_regional_parallels,
            "current_agent": "iconographic_comparator",
        }

    except Exception as exc:
        logger.exception("Error en iconographic_comparator_node")
        raise AgentExecutionError("iconographic_comparator", str(exc)) from exc
