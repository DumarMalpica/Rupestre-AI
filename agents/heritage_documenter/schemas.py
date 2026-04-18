"""Schemas Pydantic propios de AG6 — Heritage Documenter."""

from pydantic import BaseModel


class AgentInput(BaseModel):
    """Campos del estado que este agente consume como entrada."""
    # Definir según core/state.py
    pass


class AgentOutput(BaseModel):
    """Campos que este agente escribe en el estado."""
    # ficha_pdf_path
    # ficha_json
    # record_id
    pass
