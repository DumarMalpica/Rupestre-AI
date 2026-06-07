"""
Estados del flujo conversacional de Rupestre AI por WhatsApp:
  WAITING_PHOTO        → esperando foto del pictograma
  WAITING_SITE_NAME    → esperando nombre del sitio
  WAITING_MUNICIPALITY → esperando municipio y departamento
  WAITING_COORDINATES  → esperando coordenadas GPS
  WAITING_INVESTIGATOR → esperando nombre del investigador
  WAITING_ARCH_ID      → esperando número de registro de arqueólogo
  PROCESSING           → pipeline ejecutándose
  DONE                 → ficha entregada
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ConversationSession:
    phone: str
    state: str = "WAITING_PHOTO"
    image_path: Optional[str] = None
    site_name: Optional[str] = None
    municipality: Optional[str] = None
    department: Optional[str] = None
    investigator_name: Optional[str] = None
    archaeologist_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    errors: list = field(default_factory=list)


# Almacén en memoria: phone_number → ConversationSession
_sessions: dict[str, ConversationSession] = {}


def get_session(phone: str) -> ConversationSession:
    if phone not in _sessions:
        _sessions[phone] = ConversationSession(phone=phone)
    return _sessions[phone]


def reset_session(phone: str) -> None:
    _sessions[phone] = ConversationSession(phone=phone)
