"""Schemas Pydantic propios de AG3 — Iconographic Comparator."""

from pydantic import BaseModel


class AgentInput(BaseModel):
    """Campos del estado que este agente consume como entrada."""

    # Definir según core/state.py
    pass


class AgentOutput(BaseModel):
    """Campos que este agente escribe en el estado."""

    # similar_motifs
    # has_regional_parallels
    pass
