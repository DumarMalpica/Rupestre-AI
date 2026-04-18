"""Schemas Pydantic propios de AG1 — Image Processor."""

from pydantic import BaseModel


class AgentInput(BaseModel):
    """Campos del estado que este agente consume como entrada."""

    # Definir según core/state.py
    pass


class AgentOutput(BaseModel):
    """Campos que este agente escribe en el estado."""

    # enhanced_image
    # image_quality_ok
    pass
