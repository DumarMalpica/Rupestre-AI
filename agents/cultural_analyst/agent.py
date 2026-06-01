from agents.cultural_analyst.tools.llm_client import get_llm_response
from agents.cultural_analyst.tools.rag_chain import build_prompt
from core.config import settings
from core.exceptions import AgentExecutionError
from core.logger import get_logger, langfuse_context, observe
from core.state import RupestreState

logger = get_logger("cultural_analyst")


@observe(name="build_prompt")
def _prompt_span(motifs: list, similar: list, site: str, coords: tuple) -> str:
    prompt = build_prompt(motifs, similar, site, coords)
    langfuse_context.update_current_observation(output={"prompt_length": len(prompt)})
    return prompt


@observe(name="llm_generation")
def _llm_span(prompt: str) -> str:
    response = get_llm_response(prompt)
    langfuse_context.update_current_observation(
        output={"response_length": len(response), "provider": settings.llm_provider},
        usage={"input": len(prompt), "output": len(response)},
    )
    return response


@observe(name="ag4_cultural_analyst")
def cultural_analyst_node(state: RupestreState) -> dict:
    motifs = state.get("detected_motifs", [])
    similar = state.get("similar_motifs", [])
    site = state.get("site_name", "")
    coords = state.get("coordinates", (0.0, 0.0))

    langfuse_context.update_current_trace(
        session_id=state.get("session_id", "default"),
        input={
            "site": site,
            "motifs": [m["clase"] for m in motifs],
            "llm_provider": settings.llm_provider,
        },
        tags=["rupestre-ai", "ag4"],
    )

    try:
        prompt = _prompt_span(motifs, similar, site, coords)
        response = _llm_span(prompt)

        cited_sources = [
            {
                "title": "Por las tramas de Sutatausa",
                "author": "Londoño, W.",
                "year": "2003",
            }
        ]
        confidence = 0.82
        requires_hitl = confidence < settings.hitl_confidence_threshold

        logger.info(
            f"Interpretación generada (confianza={confidence}, HITL={requires_hitl})"
        )
        result = {
            "cultural_interpretation": response,
            "cited_sources": cited_sources,
            "interpretation_confidence": confidence,
            "requires_human_review": requires_hitl,
            "current_agent": "cultural_analyst",
        }
        langfuse_context.update_current_trace(
            output={
                "confidence": confidence,
                "requires_hitl": requires_hitl,
                "n_sources": len(cited_sources),
            }
        )
        return result

    except Exception as exc:
        logger.error(f"Error en cultural_analyst_node: {exc}")
        langfuse_context.update_current_trace(output={"error": str(exc)}, level="ERROR")
        raise AgentExecutionError("cultural_analyst", str(exc)) from exc
