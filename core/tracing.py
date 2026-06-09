"""Integración de LangSmith para trazar el grafo LangGraph.

LangGraph se auto-instrumenta cuando `LANGSMITH_TRACING=true` y existe
`LANGSMITH_API_KEY` (ver `core/logger.py`, que normaliza las variables al
importarse). Cada nodo del grafo (image_processor, motif_detector, …) aparece
como un sub-run anidado bajo el run raíz del pipeline.

Este módulo solo añade *contexto* a esas trazas: un nombre legible por análisis
y metadata (session_id, sitio, ubicación) para poder filtrar en el dashboard.
"""

from __future__ import annotations

import os
from typing import Any

# Import perezoso de RupestreState solo para tipado; en runtime aceptamos dict.
RupestreState = dict


def langsmith_enabled() -> bool:
    """True si el tracing de LangSmith está activo en este proceso."""
    return os.getenv("LANGSMITH_TRACING", "").lower() == "true" and bool(
        os.getenv("LANGSMITH_API_KEY")
    )


def build_run_config(state: RupestreState) -> dict[str, Any]:
    """Config de ejecución para enriquecer la traza del grafo en LangSmith.

    Se pasa como `rupestre_graph.invoke(state, config=build_run_config(state))`.
    Nombra el run raíz y adjunta metadata/tags para identificar cada análisis.
    Si el tracing está desactivado, la config es inofensiva (LangGraph la ignora).
    """
    site = state.get("site_name") or "desconocido"
    return {
        "run_name": f"rupestre · {site}",
        "tags": ["rupestre-ai", "pipeline"],
        "metadata": {
            "session_id": state.get("session_id", ""),
            "site_name": site,
            "municipality": state.get("municipality", ""),
            "department": state.get("department", ""),
        },
    }


def flush_traces() -> None:
    """Garantiza el envío de trazas pendientes antes de que el proceso termine.

    Útil en scripts cortos (CLI): bloquea hasta que los tracers de LangChain
    terminen de subir sus runs a LangSmith.
    """
    if not langsmith_enabled():
        return
    try:
        from langchain_core.tracers.langchain import wait_for_all_tracers

        wait_for_all_tracers()
    except Exception:
        pass
