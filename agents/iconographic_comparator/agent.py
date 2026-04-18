"""AG3 — Iconographic Comparator | Dev 2"""

from core.exceptions import AgentExecutionError
from core.logger import get_logger, get_tracer
from core.state import RupestreState

logger = get_logger("iconographic_comparator")


def comparator_node(state: RupestreState) -> dict:
    """
    Nodo 3 del grafo. Compara motivos detectados contra el inventario
    regional almacenado en ChromaDB.

    Lee:   detected_motifs, site_name
    Escribe: similar_motifs, has_regional_parallels
    """
    tracer = get_tracer()
    motifs = state.get("detected_motifs") or []
    logger.info(f"Comparando {len(motifs)} motivo(s) con inventario regional")

    with tracer.trace(name="iconographic_comparator"):
        try:
            # TODO: implementar tools/retriever.py y tools/scorer.py
            # results = retriever.search_similar(motifs)
            # ranked = scorer.rank(results)

            # ── PLACEHOLDER ───────────────────────────────────
            similar_motifs = [
                {
                    "motif_id": "motif_001",
                    "top_matches": [
                        {
                            "site": "Villa de Leyva — Sector Norte",
                            "score": 0.88,
                            "cultura": "Muisca",
                            "periodo": "600-1600 d.C.",
                        }
                    ],
                }
            ]
            has_regional_parallels = any(
                match["score"] > 0.75
                for m in similar_motifs
                if isinstance(m, dict)
                for match in (m.get("top_matches") or [])
                if isinstance(match, dict)
            )
            # ─────────────────────────────────────────────────

            logger.info(f"Paralelos regionales encontrados: {has_regional_parallels}")

            return {
                "similar_motifs": similar_motifs,
                "has_regional_parallels": has_regional_parallels,
                "current_agent": "comparator",
            }

        except Exception as e:
            logger.error(f"Error en comparator: {e}")
            raise AgentExecutionError("iconographic_comparator", str(e))