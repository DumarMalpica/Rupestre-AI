"""Schemas Pydantic propios de AG4 — Cultural Analyst."""

from pydantic import BaseModel


class AgentInput(BaseModel):
    """Campos del estado que este agente consume como entrada."""

    # Definir según core/state.py
    pass


class AgentOutput(BaseModel):
    """Campos que este agente escribe en el estado."""

    # cultural_interpretation
    # cited_sources
    # interpretation_confidence
    # requires_human_review
    pass
