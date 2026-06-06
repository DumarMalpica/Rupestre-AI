from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents.cultural_analyst.agent import cultural_analyst_node
from agents.heritage_documenter.agent import heritage_documenter_node
from agents.iconographic_comparator.agent import iconographic_comparator_node
from agents.image_processor.agent import image_processor_node
from agents.lama_enhancer.agent import lama_enhancer_node
from agents.motif_detector.agent import motif_detector_node
from agents.reconstructor.agent import reconstructor_node
from core.state import RupestreState


def should_continue(state: RupestreState) -> str:
    if not state.get("image_quality_ok", True):
        return END
    return "motif_detector"


def should_generate_ficha(state: RupestreState) -> str:
    if state.get("requires_human_review", False):
        return END
    return "reconstructor"


_graph = StateGraph(RupestreState)

_graph.add_node("image_processor", image_processor_node)
_graph.add_node("motif_detector", motif_detector_node)
_graph.add_node("iconographic_comparator", iconographic_comparator_node)
_graph.add_node("cultural_analyst", cultural_analyst_node)
_graph.add_node("reconstructor", reconstructor_node)
_graph.add_node("lama_enhancer", lama_enhancer_node)
_graph.add_node("heritage_documenter", heritage_documenter_node)

_graph.add_edge(START, "image_processor")
_graph.add_conditional_edges("image_processor", should_continue)
_graph.add_edge("motif_detector", "iconographic_comparator")
_graph.add_edge("iconographic_comparator", "cultural_analyst")
_graph.add_conditional_edges("cultural_analyst", should_generate_ficha)
_graph.add_edge("reconstructor", "lama_enhancer")
_graph.add_edge("lama_enhancer", "heritage_documenter")
_graph.add_edge("heritage_documenter", END)

rupestre_graph = _graph.compile()
