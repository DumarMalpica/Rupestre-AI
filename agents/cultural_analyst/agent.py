from agents.cultural_analyst.tools.corpus_retriever import retrieve_context
from agents.cultural_analyst.tools.llm_client import get_llm_response
from agents.cultural_analyst.tools.rag_chain import build_prompt
from agents.cultural_analyst.tools.vision_describer import describe_image
from core.config import settings
from core.exceptions import AgentExecutionError
from core.logger import get_logger, langfuse_context, observe
from core.state import RupestreState
from core.text_utils import clean_interpretation

logger = get_logger("cultural_analyst")


@observe(name="vision_describe")
def _vision_span(image_path: str) -> str:
    description = describe_image(image_path)
    langfuse_context.update_current_observation(
        output={"description_length": len(description), "model": settings.vision_model}
    )
    return description


@observe(name="corpus_retrieve")
def _retrieve_span(query: str) -> list[dict]:
    passages = retrieve_context(query)
    langfuse_context.update_current_observation(output={"n_passages": len(passages)})
    return passages


@observe(name="build_prompt")
def _prompt_span(
    motifs: list,
    similar: list,
    site: str,
    coords: tuple,
    description: str,
    passages: list,
) -> str:
    prompt = build_prompt(motifs, similar, site, coords, description, passages)
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


def _build_sources(passages: list[dict]) -> list[dict]:
    """Convierte los pasajes recuperados en fuentes citadas (title/author/year).

    Deduplica por documento y agrupa las páginas. Mantiene las claves que
    consume el generador de ficha (PDF/HTML).
    """
    grouped: dict[str, list] = {}
    for passage in passages:
        source = str(passage.get("source", "Corpus")).removesuffix(".pdf")
        page = passage.get("page")
        pages = grouped.setdefault(source, [])
        if page is not None and page not in pages:
            pages.append(page)

    sources = []
    for source, pages in grouped.items():
        pages_str = ", ".join(str(p) for p in sorted(pages)) if pages else "s.p."
        sources.append(
            {
                "title": f"{source} (pp. {pages_str})",
                "author": "Corpus documental ICANH",
                "year": "s.f.",
            }
        )
    return sources


def _estimate_confidence(passages: list[dict]) -> float:
    """Deriva la confianza del mejor score de recuperación (coseno ~0.3-0.7).

    Reescala a un rango interpretable [0.5, 0.95]: poca evidencia → revisión
    humana (HITL); buena evidencia → confianza alta.
    """
    if not passages:
        return 0.5
    top = max(p.get("score", 0.0) for p in passages)
    confidence = 0.5 + min(max(top, 0.0), 0.8) * 0.5
    return round(min(confidence, 0.95), 2)


@observe(name="ag4_cultural_analyst")
def cultural_analyst_node(state: RupestreState) -> dict:
    motifs = state.get("detected_motifs", [])
    similar = state.get("similar_motifs", [])
    site = state.get("site_name", "")
    coords = state.get("coordinates", (0.0, 0.0))
    image_path = state.get("enhanced_image") or state.get("image_path", "")

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
        description = _vision_span(image_path)

        # Consulta al corpus: descripción visual + clases detectadas por YOLO
        clases = " ".join(m["clase"] for m in motifs)
        query = f"{description} {clases}".strip()
        passages = _retrieve_span(query)

        prompt = _prompt_span(motifs, similar, site, coords, description, passages)
        response = clean_interpretation(_llm_span(prompt))

        cited_sources = _build_sources(passages)
        confidence = _estimate_confidence(passages)
        requires_hitl = confidence < settings.hitl_confidence_threshold

        logger.info(
            f"Interpretación generada (confianza={confidence}, HITL={requires_hitl}, "
            f"pasajes={len(passages)})"
        )
        result = {
            "image_description": description,
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
