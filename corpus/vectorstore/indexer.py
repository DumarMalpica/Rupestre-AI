from __future__ import annotations

from corpus.vectorstore.chroma_client import get_collection

_BATCH_SIZE = 50


def index_documents(chunks: list[dict], collection_name: str) -> int:
    if not chunks:
        return 0

    collection = get_collection(collection_name)
    total = 0

    for i in range(0, len(chunks), _BATCH_SIZE):
        batch = chunks[i : i + _BATCH_SIZE]

        ids = [c["chunk_id"] for c in batch]
        documents = [c["text"] for c in batch]
        metadatas = [{"source": c["source"], "page": c["page"]} for c in batch]

        # upsert es idempotente: reindexar el mismo chunk_id actualiza sin duplicar
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        total += len(batch)

    return total
