from agents.iconographic_comparator.tools.retriever import retrieve_similar
from core.exceptions import AgentExecutionError
from core.logger import get_logger, langfuse_context, observe
from core.state import RupestreState

logger = get_logger("iconographic_comparator")


@observe(name="chroma_retrieve")
def _retrieve_span(motifs: list[dict]) -> tuple[list[dict], bool]:
    similar_motifs = []
    for motif in motifs:
        matches = retrieve_similar(motif)
        similar_motifs.append({"motif_id": motif["id"], "top_matches": matches})

    has_parallels = any(
        m["score"] > 0.75 for sm in similar_motifs for m in sm.get("top_matches", [])
    )
    langfuse_context.update_current_observation(
        output={"has_parallels": has_parallels, "n_results": len(similar_motifs)}
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
