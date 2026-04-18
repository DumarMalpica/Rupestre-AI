"""Schemas Pydantic propios de AG2 — Motif Detector."""

from pydantic import BaseModel


class AgentInput(BaseModel):
    """Campos del estado que este agente consume como entrada."""

    # Definir según core/state.py
    pass


class AgentOutput(BaseModel):
    """Campos que este agente escribe en el estado."""

    # detected_motifs
    # motif_count
    pass
