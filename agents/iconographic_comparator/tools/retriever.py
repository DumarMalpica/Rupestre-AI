from __future__ import annotations

from core.config import settings
from core.logger import get_logger

logger = get_logger("iconographic_comparator.retriever")

_MOCK_MATCH = [
    {
        "site": "Villa de Leyva — Sector Norte",
        "score": 0.88,
        "cultura": "Muisca",
        "periodo": "600-1600 d.C.",
    }
]


def retrieve_similar(motif: dict, n_results: int = 3) -> list[dict]:
    if not settings.mongo_uri:
        return _MOCK_MATCH

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
            return _MOCK_MATCH

        query_vec = np.asarray(
            embed_text(f"motivo rupestre {motif.get('clase', '')}"), dtype=np.float32
        )
        matrix = np.asarray([d["embedding"] for d in docs], dtype=np.float32)
        scores = matrix @ query_vec  # vectores normalizados → coseno
        top_idx = np.argsort(scores)[::-1][:n_results]

        matches = []
        for i in top_idx:
            doc = docs[int(i)]
            matches.append(
                {
                    "site": doc.get("source", "desconocido"),
                    "score": round(float(scores[int(i)]), 4),
                    "cultura": doc.get("cultura", "desconocida"),
                    "periodo": doc.get("periodo", "desconocido"),
                }
            )
        return matches

    except Exception as exc:
        logger.warning(f"Retrieval iconográfico falló ({exc}) — usando mock")
        return _MOCK_MATCH
