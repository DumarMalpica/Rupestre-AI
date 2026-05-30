from __future__ import annotations

from pathlib import Path


def load_pdf(pdf_path: str) -> list[dict]:
    import fitz  # PyMuPDF

    filename = Path(pdf_path).name
    pages: list[dict] = []

    doc = fitz.open(pdf_path)
    try:
        for page_num in range(len(doc)):
            text = doc[page_num].get_text().strip()
            if len(text) < 50:
                continue
            pages.append({"page": page_num + 1, "text": text, "source": filename})
    finally:
        doc.close()

    return pages
