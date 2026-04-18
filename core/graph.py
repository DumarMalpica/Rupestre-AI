"""
Grafo LangGraph — Clasificador central del sistema.
Conecta los 6 agentes y define el flujo de ejecución.
"""

from langgraph.graph import StateGraph, END

from core.state import RupestreState
from agents.image_processor.agent import image_processor_node
from agents.motif_detector.agent import motif_detector_node
from agents.iconographic_comparator.agent import comparator_node
from agents.cultural_analyst.agent import cultural_analyst_node
from agents.reconstructor.agent import reconstructor_node
from agents.heritage_documenter.agent import documenter_node


def _route_after_image_processor(state: RupestreState) -> str:
    """
    Bifurcación post AG1:
    - Si la imagen no tiene calidad → terminar el grafo
    - Si la imagen es válida → continuar a detección de motivos
    """
    if not state.get("image_quality_ok", False):
        return "end"
    return "motif_detector"


def _route_after_cultural_analyst(state: RupestreState) -> str:
    """
    Bifurcación post AG4:
    - Si requiere revisión humana (HITL) → terminar y notificar
    - Si confidence OK → continuar a reconstrucción GAN
    """
    if state.get("requires_human_review", False):
        return "end"
    return "reconstructor"


def build_graph() -> StateGraph:
    """Construye y compila el grafo LangGraph del sistema."""
    graph = StateGraph(RupestreState)

    # ── Registrar nodos ───────────────────────────────────────
    graph.add_node("image_processor", image_processor_node)
    graph.add_node("motif_detector", motif_detector_node)
    graph.add_node("comparator", comparator_node)
    graph.add_node("cultural_analyst", cultural_analyst_node)
    graph.add_node("reconstructor", reconstructor_node)
    graph.add_node("documenter", documenter_node)

    # ── Entry point ───────────────────────────────────────────
    graph.set_entry_point("image_processor")

    # ── Aristas condicionales ─────────────────────────────────
    graph.add_conditional_edges(
        "image_processor",
        _route_after_image_processor,
        {"motif_detector": "motif_detector", "end": END},
    )

    # ── Aristas lineales ──────────────────────────────────────
    graph.add_edge("motif_detector", "comparator")
    graph.add_edge("comparator", "cultural_analyst")

    graph.add_conditional_edges(
        "cultural_analyst",
        _route_after_cultural_analyst,
        {"reconstructor": "reconstructor", "end": END},
    )

    graph.add_edge("reconstructor", "documenter")
    graph.add_edge("documenter", END)

    return graph.compile()


# Instancia global del grafo
rupestre_graph = build_graph()
