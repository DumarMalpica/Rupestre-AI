"""Cliente singleton para ChromaDB."""

import chromadb
from core.config import settings
from core.logger import get_logger

logger = get_logger("corpus.chroma_client")

_client = None
_collections = {}


def get_client() -> chromadb.Client:
    """Retorna el cliente ChromaDB (singleton)."""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_path)
        logger.info(f"ChromaDB conectado en: {settings.chroma_path}")
    return _client


def get_collection(name: str):
    """Retorna o crea una colección ChromaDB."""
    global _collections
    if name not in _collections:
        client = get_client()
        _collections[name] = client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"Colección lista: {name}")
    return _collections[name]
