from __future__ import annotations

from core.config import settings
from core.logger import get_logger

logger = get_logger("cultural_analyst.corpus_retriever")

_MOCK_PASSAGES = [
    {
        "text": (
            "Los petroglifos muiscas de la región de Sutatausa presentan motivos "
            "en espiral asociados a calendarios rituales y marcadores solsticiales "
            "(Londoño, 2003)."
        ),
        "source": "Por las tramas de Sutatausa",
        "page": 12,
        "score": 0.80,
    }
]


def retrieve_context(query: str, n_results: int | None = None) -> list[dict]:
    """Recupera los pasajes del corpus más similares a la consulta.

    Embebe el query, calcula similitud coseno en memoria sobre los vectores de
    MongoDB y devuelve los top-k pasajes con su fuente y página. Cae a un pasaje
    mock si Mongo no está configurado, está vacío o falla.
    """
    n_results = n_results or settings.corpus_top_k

    if not settings.mongo_uri:
        return _MOCK_PASSAGES

    try:
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
            return _MOCK_PASSAGES

        query_vec = np.asarray(embed_text(query), dtype=np.float32)
        matrix = np.asarray([d["embedding"] for d in docs], dtype=np.float32)
        scores = matrix @ query_vec  # vectores normalizados → coseno
        top_idx = np.argsort(scores)[::-1][:n_results]

        passages = []
        for i in top_idx:
            doc = docs[int(i)]
            passages.append(
                {
                    "text": doc.get("text", ""),
                    "source": doc.get("source", "desconocido"),
                    "page": doc.get("page", 0),
                    "score": round(float(scores[int(i)]), 4),
                }
            )
        return passages

    except Exception as exc:
        logger.warning(f"Retrieval de corpus falló ({exc}) — usando mock")
        return _MOCK_PASSAGES
