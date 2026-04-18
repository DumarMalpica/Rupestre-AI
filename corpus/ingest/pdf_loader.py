"""Carga PDFs académicos del ICANH y tesis UPTC con PyMuPDF."""

from pathlib import Path
from typing import Generator
from core.logger import get_logger

logger = get_logger("corpus.pdf_loader")


def load_pdf(path: str) -> list[dict]:
    """
    Extrae texto y metadatos de un PDF académico.

    Returns:
        Lista de dicts con keys: text, page, source, metadata
    """
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(path)
        pages = []
        for i, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                pages.append({
                    "text": text,
                    "page": i + 1,
                    "source": Path(path).name,
                    "metadata": {
                        "source_type": "pdf",
                        "file": path,
                        "page": i + 1,
                        "total_pages": len(doc),
                    },
                })
        logger.info(f"PDF cargado: {path} — {len(pages)} páginas con texto")
        return pages

    except ImportError:
        logger.warning("PyMuPDF no instalado. Instalar con: pip install pymupdf")
        return []
    except Exception as e:
        logger.error(f"Error cargando PDF {path}: {e}")
        return []


def load_directory(directory: str, extension: str = ".pdf") -> list[dict]:
    """Carga todos los PDFs de un directorio."""
    docs = []
    for path in Path(directory).rglob(f"*{extension}"):
        docs.extend(load_pdf(str(path)))
    logger.info(f"Directorio cargado: {len(docs)} páginas totales")
    return docs
