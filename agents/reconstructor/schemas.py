"""Schemas Pydantic propios de AG5 — Reconstructor."""

from pydantic import BaseModel


class AgentInput(BaseModel):
    """Campos del estado que este agente consume como entrada."""

    # Definir según core/state.py
    pass


class AgentOutput(BaseModel):
    """Campos que este agente escribe en el estado."""

    # reconstructed_image
    # confidence_map
    # reconstruction_applied
    pass
