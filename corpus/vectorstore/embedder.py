from __future__ import annotations

from functools import lru_cache

from core.logger import get_logger

logger = get_logger("vectorstore.embedder")

# Multilingüe, óptimo para español. 384 dimensiones.
# Primera invocación descarga ~1.1 GB; se cachea en ~/.cache/huggingface/
_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer

    logger.info(f"Cargando modelo de embeddings {_MODEL_NAME}")
    return SentenceTransformer(_MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embeddings normalizados (norma L2 = 1) → coseno equivale a producto punto."""
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    return vectors.tolist()


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]
