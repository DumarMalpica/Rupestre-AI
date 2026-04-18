"""
Observabilidad centralizada con LangFuse.
Todos los agentes importan get_tracer() desde aquí.
Si se cambia la herramienta de trazas, solo se modifica este archivo.
"""

import logging
from typing import Optional

from core.config import settings

# Logger estándar de Python (siempre disponible)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("rupestre-ai")


def get_logger(name: str) -> logging.Logger:
    """Retorna un logger con el nombre del módulo."""
    return logging.getLogger(f"rupestre-ai.{name}")


# ── LangFuse (lazy init para no fallar si no está configurado) ──
_langfuse_client = None


def get_tracer():
    """
    Retorna el cliente LangFuse para trazas de agentes y RAG.
    Si LangFuse no está configurado, retorna un tracer mock.
    """
    global _langfuse_client

    if _langfuse_client is not None:
        return _langfuse_client

    if settings.langfuse_public_key.startswith("pk-test"):
        logger.warning("LangFuse en modo mock — trazas no se enviarán")
        _langfuse_client = _MockTracer()
        return _langfuse_client

    try:
        from langfuse import Langfuse

        _langfuse_client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )
        logger.info("LangFuse conectado correctamente")
    except Exception as e:
        logger.warning(f"LangFuse no disponible: {e}. Usando mock.")
        _langfuse_client = _MockTracer()

    return _langfuse_client


class _MockTracer:
    """Tracer mock cuando LangFuse no está disponible (desarrollo/tests)."""

    def trace(self, **kwargs):
        return self

    def span(self, **kwargs):
        return self

    def update(self, **kwargs):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass
