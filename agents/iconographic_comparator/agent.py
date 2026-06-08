from agents.iconographic_comparator.tools.parallel_finder import find_regional_parallels
from core.exceptions import AgentExecutionError
from core.logger import get_logger, langfuse_context, observe
from core.state import RupestreState

logger = get_logger("iconographic_comparator")


@observe(name="parallel_search")
def _retrieve_span(motifs: list[dict]) -> tuple[list[dict], bool]:
    # Paralelos consolidados para todo el panel (máx. settings.max_regional_parallels),
    # con sitio/cultura/período reales extraídos del corpus por Claude.
    parallels = find_regional_parallels(motifs)
    similar_motifs = (
        [{"motif_id": "panel", "top_matches": parallels}] if parallels else []
    )
    has_parallels = bool(parallels)
    langfuse_context.update_current_observation(
        output={"has_parallels": has_parallels, "n_parallels": len(parallels)}
    )
    return similar_motifs, has_parallels


@observe(name="ag3_iconographic_comparator")
def iconographic_comparator_node(state: RupestreState) -> dict:
    langfuse_context.update_current_trace(
        session_id=state.get("session_id", "default"),
        input={
            "motif_count": state.get("motif_count", 0),
            "site_name": state.get("site_name"),
        },
        tags=["rupestre-ai", "ag3"],
    )

    try:
        motifs = state.get("detected_motifs", [])

        similar_motifs, has_parallels = _retrieve_span(motifs)

        logger.info(f"Comparación: {len(motifs)} motivos, paralelos={has_parallels}")
        result = {
            "similar_motifs": similar_motifs,
            "has_regional_parallels": has_parallels,
            "current_agent": "iconographic_comparator",
        }
        langfuse_context.update_current_trace(
            output={
                "has_regional_parallels": has_parallels,
                "n_similar": len(similar_motifs),
            }
        )
        return result

    except Exception as exc:
        logger.error(f"Error en iconographic_comparator_node: {exc}")
        langfuse_context.update_current_trace(output={"error": str(exc)}, level="ERROR")
        raise AgentExecutionError("iconographic_comparator", str(exc)) from exc
