from __future__ import annotations

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from core.config import settings

# Primera invocación descarga ~1.1 GB del modelo; se cachea en ~/.cache/huggingface/
_embedding_fn = SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)


def get_collection(collection_name: str) -> chromadb.Collection:
    client = chromadb.PersistentClient(path=settings.chromadb_path)
    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=_embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )
