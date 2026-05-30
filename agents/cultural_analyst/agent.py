from __future__ import annotations

from core.config import settings
from core.exceptions import AgentExecutionError
from core.logger import get_logger
from core.state import RupestreState

from agents.cultural_analyst.tools.llm_client import get_llm_response
from agents.cultural_analyst.tools.rag_chain import build_prompt
from agents.cultural_analyst.tools.source_validator import validate_sources

logger = get_logger("cultural_analyst")

_DEFAULT_SOURCES = [
    {
        "title": "Por las tramas de Sutatausa",
        "author": "Londoño, W.",
        "year": "2003",
    }
]


def cultural_analyst_node(state: RupestreState) -> dict:
    try:
        prompt = build_prompt(
            detected_motifs=state.get("detected_motifs", []),
            similar_motifs=state.get("similar_motifs", []),
            site_name=state.get("site_name", "Sitio desconocido"),
            coordinates=state.get("coordinates", (0.0, 0.0)),
        )

        interpretation = get_llm_response(prompt)
        cited_sources = validate_sources(list(_DEFAULT_SOURCES))

        interpretation_confidence: float = 0.82
        requires_human_review = (
            interpretation_confidence < settings.hitl_confidence_threshold
        )

        logger.info(
            "Interpretación cultural generada (confianza=%.2f, HITL=%s)",
            interpretation_confidence,
            requires_human_review,
        )

        return {
            "cultural_interpretation": interpretation,
            "cited_sources": cited_sources,
            "interpretation_confidence": interpretation_confidence,
            "requires_human_review": requires_human_review,
            "current_agent": "cultural_analyst",
        }

    except Exception as exc:
        logger.exception("Error en cultural_analyst_node")
        raise AgentExecutionError("cultural_analyst", str(exc)) from exc
