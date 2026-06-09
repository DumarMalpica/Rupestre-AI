import atexit
import logging
import os

from dotenv import load_dotenv

load_dotenv()

# El SDK v4 lee LANGFUSE_HOST; si el .env usa LANGFUSE_BASE_URL lo mapeamos.
if os.getenv("LANGFUSE_BASE_URL") and not os.getenv("LANGFUSE_HOST"):
    os.environ["LANGFUSE_HOST"] = os.environ["LANGFUSE_BASE_URL"]

# ─── LangSmith (trazas del grafo LangGraph) ──────────────────────────────────
# LangGraph se auto-instrumenta cuando LANGSMITH_TRACING=true y hay API key:
# cada nodo (agente) y cada paso del flujo se envían como sub-run a LangSmith.
# Mapeamos además los alias legacy LANGCHAIN_* por compatibilidad.
if os.getenv("LANGSMITH_TRACING", "").lower() == "true" and os.getenv(
    "LANGSMITH_API_KEY"
):
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_API_KEY", os.environ["LANGSMITH_API_KEY"])
    if os.getenv("LANGSMITH_ENDPOINT"):
        os.environ.setdefault("LANGCHAIN_ENDPOINT", os.environ["LANGSMITH_ENDPOINT"])
    if os.getenv("LANGSMITH_PROJECT"):
        os.environ.setdefault("LANGCHAIN_PROJECT", os.environ["LANGSMITH_PROJECT"])

try:
    from langfuse import Langfuse
    from langfuse.decorators import langfuse_context, observe

    _pk = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    _sk = os.getenv("LANGFUSE_SECRET_KEY", "")
    _host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if _pk and _sk and "your" not in _pk and len(_pk) >= 10:
        # Inicializar el cliente global que usa @observe.
        # flush_at=1 → envía cada evento inmediatamente (crítico en scripts cortos).
        Langfuse(public_key=_pk, secret_key=_sk, host=_host, flush_at=1)
        atexit.register(langfuse_context.flush)

except ImportError:

    class _NoOpCtx:
        def update_current_trace(self, **kw):
            pass

        def update_current_observation(self, **kw):
            pass

        def flush(self):
            pass

    langfuse_context = _NoOpCtx()  # type: ignore[assignment]

    def observe(func=None, **kw):  # type: ignore[misc]
        return func if func is not None else (lambda f: f)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
