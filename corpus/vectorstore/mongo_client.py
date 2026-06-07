from __future__ import annotations

from functools import lru_cache

from core.config import settings
from core.logger import get_logger

logger = get_logger("vectorstore.mongo")


@lru_cache(maxsize=1)
def _get_client():
    from pymongo import MongoClient

    uri = settings.mongo_uri
    if not uri:
        raise RuntimeError("MONGO_URL / MONGO_PUBLIC_URL no configurado")
    logger.info("Conectando a MongoDB")
    return MongoClient(uri, serverSelectionTimeoutMS=5000)


def get_collection(name: str | None = None):
    """Devuelve la colección de Mongo del corpus vectorizado."""
    collection_name = name or settings.mongo_collection
    client = _get_client()
    return client[settings.mongo_db][collection_name]
