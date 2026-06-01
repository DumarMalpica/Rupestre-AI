from __future__ import annotations

from core.config import settings
from core.logger import get_logger

logger = get_logger("cultural_analyst.llm_client")

_MOCK_RESPONSE = (
    "Los motivos en espiral registrados en este sitio presentan "
    "características propias del período Muisca tardío (600-1600 d.C.). "
    "La orientación hacia el solsticio de verano sugiere función "
    "calendárica-ritual, consistente con los registros de Sutatausa "
    "(Londoño, 2003). La superposición de trazos indica uso prolongado "
    "del sitio como espacio sagrado comunitario."
)


def get_llm_response(prompt: str) -> str:
    provider = settings.llm_provider

    if provider == "mock":
        return _MOCK_RESPONSE

    try:
        if provider == "ollama":
            import requests

            response = requests.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=120,
            )
            response.raise_for_status()
            return response.json()["response"]

        if provider == "openai":
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(model="gpt-4o", api_key=settings.openai_api_key)
            return llm.invoke(prompt).content

    except Exception:
        logger.warning("LLM provider '%s' falló, usando respuesta mock", provider)

    return _MOCK_RESPONSE
