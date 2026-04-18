"""Pipeline de indexación: chunks → embeddings → ChromaDB."""

import uuid
from corpus.vectorstore.chroma_client import get_collection
from core.logger import get_logger

logger = get_logger("corpus.indexer")

COLLECTION_NAME = "corpus_rupestre"
EMBEDDING_MODEL = "intfloat/multilingual-e5-large"


def get_embedder():
    """Carga el modelo de embeddings (lazy)."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBEDDING_MODEL)


def index_chunks(chunks: list[dict]) -> int:
    """
    Indexa una lista de chunks en ChromaDB.

    Returns:
        Número de chunks indexados exitosamente.
    """
    if not chunks:
        logger.warning("No hay chunks para indexar")
        return 0

    logger.info(f"Indexando {len(chunks)} chunks...")
    embedder = get_embedder()
    collection = get_collection(COLLECTION_NAME)

    texts = [c["text"] for c in chunks]
    metadatas = [c.get("metadata", {}) for c in chunks]
    ids = [str(uuid.uuid4()) for _ in chunks]

    embeddings = embedder.encode(texts, show_progress_bar=True).tolist()

    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )

    logger.info(f"{len(chunks)} chunks indexados en '{COLLECTION_NAME}'")
    return len(chunks)


def query(text: str, n_results: int = 5) -> list[dict]:
    """Busca fragmentos similares al texto dado."""
    embedder = get_embedder()
    collection = get_collection(COLLECTION_NAME)
    embedding = embedder.encode([text]).tolist()

    results = collection.query(
        query_embeddings=embedding,
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    return [
        {
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "score": 1 - results["distances"][0][i],
        }
        for i in range(len(results["documents"][0]))
    ]
