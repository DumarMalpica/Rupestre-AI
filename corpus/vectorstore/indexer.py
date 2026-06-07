from __future__ import annotations

from corpus.vectorstore.embedder import embed_texts
from corpus.vectorstore.mongo_client import get_collection

_BATCH_SIZE = 50


def index_documents(chunks: list[dict], collection_name: str | None = None) -> int:
    """Embebe los chunks y los inserta (upsert) en MongoDB.

    Cada documento: {chunk_id, text, source, page, embedding[384]}.
    El upsert por chunk_id es idempotente: reindexar actualiza sin duplicar.
    """
    if not chunks:
        return 0

    from pymongo import UpdateOne

    collection = get_collection(collection_name)
    collection.create_index("chunk_id", unique=True)

    total = 0
    for i in range(0, len(chunks), _BATCH_SIZE):
        batch = chunks[i : i + _BATCH_SIZE]
        vectors = embed_texts([c["text"] for c in batch])

        ops = [
            UpdateOne(
                {"chunk_id": c["chunk_id"]},
                {
                    "$set": {
                        "chunk_id": c["chunk_id"],
                        "text": c["text"],
                        "source": c["source"],
                        "page": c["page"],
                        "embedding": vec,
                    }
                },
                upsert=True,
            )
            for c, vec in zip(batch, vectors)
        ]
        collection.bulk_write(ops, ordered=False)
        total += len(batch)

    return total
