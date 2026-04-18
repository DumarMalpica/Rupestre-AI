"""Configuración específica de AG5 — Reconstructor."""

from pydantic_settings import BaseSettings
from core.config import settings as global_settings


class AgentConfig(BaseSettings):
    """Parámetros configurables del agente."""

    # TODO: agregar parámetros específicos del agente
    pass


agent_config = AgentConfig()
