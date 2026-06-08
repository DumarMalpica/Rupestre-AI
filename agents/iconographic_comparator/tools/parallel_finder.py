"""Paralelos iconográficos regionales reales a partir del corpus documental.

En vez de devolver el nombre del PDF como "sitio" (lo que hacía el retriever
anterior), recupera los pasajes del corpus más afines a los tipos de motivo
detectados y le pide a Claude que extraiga paralelos concretos: sitio/región,
cultura y período, citados en esos pasajes. Devuelve como máximo
`settings.max_regional_parallels` paralelos para todo el panel (no por motivo).

Cae a un mock si no hay Mongo, y a una referencia bibliográfica del corpus si no
hay proveedor anthropic. Nunca rompe el pipeline.
"""

from __future__ import annotations

import json
import re

from core.config import settings
from core.logger import get_logger

logger = get_logger("iconographic_comparator.parallel_finder")

_MOCK = [
    {
        "site": "Villa de Leyva — Sector Norte",
        "score": 0.88,
        "cultura": "Muisca",
        "periodo": "600-1600 d.C.",
    }
]


def _retrieve_passages(clases: list[str], k: int = 6) -> list[tuple[dict, float]]:
    """Top-k pasajes del corpus por similitud coseno a los tipos de motivo."""
    import numpy as np

    from corpus.vectorstore.embedder import embed_text
    from corpus.vectorstore.mongo_client import get_collection

    collection = get_collection()
    docs = list(
        collection.find(
            {}, {"text": 1, "source": 1, "page": 1, "embedding": 1, "_id": 0}
        )
    )
    if not docs:
        return []

    query = "arte rupestre motivos " + ", ".join(clases) if clases else "arte rupestre"
    query_vec = np.asarray(embed_text(query), dtype=np.float32)
    matrix = np.asarray([d["embedding"] for d in docs], dtype=np.float32)
    scores = matrix @ query_vec
    top_idx = np.argsort(scores)[::-1][:k]
    return [(docs[int(i)], float(scores[int(i)])) for i in top_idx]


def _parse_array(text: str) -> list:
    try:
        data = json.loads(text)
        return data if isinstance(data, list) else []
    except Exception:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                return data if isinstance(data, list) else []
            except Exception:
                return []
    return []


def _extract_with_claude(
    passages: list[tuple[dict, float]], clases: list[str], max_results: int
) -> list[dict]:
    import anthropic

    context = "\n\n".join(
        f"[{i}] ({doc.get('source', '?')} p.{doc.get('page', '?')}): "
        f"{str(doc.get('text', ''))[:700]}"
        for i, (doc, _) in enumerate(passages)
    )
    prompt = (
        "Eres un arqueólogo especialista en arte rupestre colombiano. Abajo hay "
        "pasajes del corpus documental (pueden estar fragmentados por OCR). "
        f"Identifica hasta {max_results} SITIOS o REGIONES de arte rupestre "
        "nombrados en los pasajes que sirvan como paralelo regional para un panel "
        f"con estos motivos: {', '.join(clases) or 'varios'}.\n\n"
        f"PASAJES:\n{context}\n\n"
        "Reglas:\n"
        "- 'sitio' debe ser un lugar o región realmente nombrado en los pasajes "
        "(p.ej. Sáchica, Sutatausa, Serranía de la Lindosa, Chiribiquete). NO "
        "inventes lugares que no aparezcan.\n"
        "- 'cultura' y 'periodo': usa lo que digan los pasajes; si no lo "
        "especifican, pon 'No especificado'.\n"
        "- 'relevancia': 0.0-1.0 según la afinidad con los motivos.\n"
        'Devuelve SOLO un arreglo JSON de objetos {"sitio","cultura","periodo",'
        '"relevancia"}. Devuelve [] únicamente si ningún pasaje nombra un sitio '
        "o región."
    )

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = next((b.text for b in response.content if b.type == "text"), "")

    parallels: list[dict] = []
    for item in _parse_array(text):
        site = str(item.get("sitio", "")).strip()
        if not site:
            continue
        try:
            score = round(max(0.0, min(1.0, float(item.get("relevancia", 0.0)))), 2)
        except Exception:
            score = 0.0
        parallels.append(
            {
                "site": site,
                "score": score,
                "cultura": str(item.get("cultura", "desconocida")).strip()
                or "desconocida",
                "periodo": str(item.get("periodo", "desconocido")).strip()
                or "desconocido",
            }
        )
    return parallels[:max_results]


def find_regional_parallels(
    motifs: list[dict], max_results: int | None = None
) -> list[dict]:
    """Devuelve hasta `max_results` paralelos regionales para todo el panel."""
    max_results = max_results or settings.max_regional_parallels

    if not motifs:
        return []

    clases: list[str] = []
    for motif in motifs:
        clase = str(motif.get("clase", "")).strip()
        if clase and clase.lower() != "motivo sin clasificar" and clase not in clases:
            clases.append(clase)

    if not settings.mongo_uri:
        return _MOCK[:max_results]

    try:
        passages = _retrieve_passages(clases)
        if not passages:
            return _MOCK[:max_results]

        if settings.llm_provider == "anthropic" and settings.anthropic_api_key:
            parallels = _extract_with_claude(passages, clases, max_results)
            if parallels:
                logger.info(f"Paralelos extraídos por Claude: {len(parallels)}")
                return parallels

        # Fallback sin LLM: referencia bibliográfica del corpus (honesto).
        fallback: list[dict] = []
        seen: set[str] = set()
        for doc, score in passages:
            source = str(doc.get("source", "")).removesuffix(".pdf")
            if source in seen:
                continue
            seen.add(source)
            fallback.append(
                {
                    "site": f"{source} (referencia documental)",
                    "score": round(score, 2),
                    "cultura": "ver fuente",
                    "periodo": "ver fuente",
                }
            )
            if len(fallback) >= max_results:
                break
        return fallback or _MOCK[:max_results]

    except Exception as exc:
        logger.warning(f"Búsqueda de paralelos falló ({exc}) — usando mock")
        return _MOCK[:max_results]
