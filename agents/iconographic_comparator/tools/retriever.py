from __future__ import annotations

from core.config import settings

_MOCK_MATCH = [
    {
        "site": "Villa de Leyva — Sector Norte",
        "score": 0.88,
        "cultura": "Muisca",
        "periodo": "600-1600 d.C.",
    }
]


def retrieve_similar(motif: dict, n_results: int = 3) -> list[dict]:
    try:
        from chromadb import PersistentClient

        client = PersistentClient(path=settings.chromadb_path)
        collection = client.get_collection(settings.chromadb_collection)

        query_text = f"motivo rupestre {motif.get('clase', '')}"
        raw = collection.query(query_texts=[query_text], n_results=n_results)

        ids = raw.get("ids", [[]])[0]
        distances = raw.get("distances", [[]])[0]
        metadatas = raw.get("metadatas", [[]])[0]

        if not ids:
            return _MOCK_MATCH

        matches = []
        for _id, dist, meta in zip(ids, distances, metadatas):
            matches.append(
                {
                    "site": meta.get("site", _id),
                    "score": round(1.0 - float(dist), 4),
                    "cultura": meta.get("cultura", "desconocida"),
                    "periodo": meta.get("periodo", "desconocido"),
                }
            )
        return matches

    except Exception:
        return _MOCK_MATCH
