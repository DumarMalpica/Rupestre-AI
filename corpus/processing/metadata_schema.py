"""Schema Pydantic para metadatos del corpus arqueológico."""

from typing import Optional
from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    """Metadatos estandarizados para cada fragmento del corpus."""
    source_type: str                    # pdf | audio_transcription | ocr
    file: str                           # ruta o nombre del archivo original
    author: Optional[str] = None        # autor del documento
    year: Optional[int] = None          # año de publicación
    institution: Optional[str] = None   # ICANH, UPTC, UNAL, etc.
    site_name: Optional[str] = None     # sitio arqueológico referenciado
    document_type: Optional[str] = None # publicacion | tesis | informe | oral
    page: Optional[int] = None          # número de página (para PDFs)
    chunk_index: Optional[int] = None   # índice del chunk dentro del documento
    language: Optional[str] = "es"
