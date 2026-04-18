"""Segmenta documentos en chunks para indexación en ChromaDB."""

from core.logger import get_logger

logger = get_logger("corpus.chunker")

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Divide documentos en fragmentos con overlap semántico.

    Args:
        documents: lista de dicts con key 'text' y 'metadata'

    Returns:
        Lista de chunks listos para indexar
    """
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        chunks = []
        for doc in documents:
            texts = splitter.split_text(doc["text"])
            for i, text in enumerate(texts):
                chunks.append(
                    {
                        "text": text,
                        "metadata": {
                            **doc.get("metadata", {}),
                            "chunk_index": i,
                            "total_chunks": len(texts),
                        },
                    }
                )

        logger.info(f"{len(documents)} documentos → {len(chunks)} chunks")
        return chunks

    except ImportError:
        logger.warning("LangChain no instalado.")
        return []
