from __future__ import annotations

import re
from pathlib import Path

_SEPARATORS = ["\n\n", "\n", " "]


def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if len(text) <= chunk_size:
        stripped = text.strip()
        return [stripped] if stripped else []

    result: list[str] = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        if end == len(text):
            chunk = text[start:].strip()
            if chunk:
                result.append(chunk)
            break

        # Find the best split point using preferred separators
        split_point = end
        for sep in _SEPARATORS:
            idx = text.rfind(sep, start + chunk_size // 3, end)
            if idx > start:
                split_point = idx + len(sep)
                break

        chunk = text[start:split_point].strip()
        if chunk:
            result.append(chunk)

        # Advance with overlap, preventing infinite loops
        next_start = split_point - overlap
        start = next_start if next_start > start else split_point

    return result


def _safe_id(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", value)


def chunk_documents(
    pages: list[dict],
    chunk_size: int = 800,
    overlap: int = 150,
) -> list[dict]:
    chunks: list[dict] = []

    for page in pages:
        text: str = page["text"]
        source: str = page["source"]
        page_num: int = page["page"]

        text_chunks = _split_text(text, chunk_size, overlap)
        stem = _safe_id(Path(source).stem)

        for idx, chunk_text in enumerate(text_chunks):
            chunk_id = f"{stem}_{page_num}_{idx}"
            chunks.append(
                {
                    "text": chunk_text,
                    "source": source,
                    "page": page_num,
                    "chunk_id": chunk_id,
                }
            )

    return chunks
