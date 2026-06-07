"""Ingesta de PDFs del corpus rupestre hacia MongoDB (vector store).

Corriendo en local, exporta MONGO_PUBLIC_URL (proxy TCP de Railway) para que
el cliente encuentre la base. Dentro de Railway usa MONGO_URL automáticamente.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Permite ejecutar el script directamente (python scripts/ingest_corpus.py)
# agregando la raíz del proyecto al sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Archivos excluidos por calidad o licencia
_SKIP_FILES: frozenset[str] = frozenset(
    {
        "el archivo y las voces del silencio (2992.pdf)",
    }
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Indexa PDFs de arte rupestre en MongoDB"
    )
    parser.add_argument(
        "--source",
        default="data/icanh_docs/rupestre",
        help="Directorio raíz con los PDFs (default: data/icanh_docs/rupestre)",
    )
    parser.add_argument(
        "--collection",
        default="corpus_rupestre",
        help="Nombre de la colección MongoDB (default: corpus_rupestre)",
    )
    args = parser.parse_args()

    source_dir = Path(args.source)
    if not source_dir.exists():
        print(f"Error: el directorio '{source_dir}' no existe.", file=sys.stderr)
        sys.exit(1)

    pdf_files = sorted(source_dir.rglob("*.pdf"))
    if not pdf_files:
        print(f"No se encontraron PDFs en '{source_dir}'.", file=sys.stderr)
        sys.exit(1)

    from corpus.ingest.pdf_loader import load_pdf
    from corpus.processing.chunker import chunk_documents
    from corpus.vectorstore.indexer import index_documents

    grand_total = 0

    for pdf_path in pdf_files:
        if pdf_path.name in _SKIP_FILES:
            print(f"⏭  Omitido (lista de exclusión): {pdf_path.name}")
            continue

        try:
            pages = load_pdf(str(pdf_path))
            if not pages:
                print(f"⚠  Sin texto extraíble: {pdf_path.name}")
                continue

            chunks = chunk_documents(pages)
            n = index_documents(chunks, args.collection)
            grand_total += n
            print(f"✅ {pdf_path.name}: {n} chunks indexados")

        except Exception as exc:
            print(f"❌ Error procesando {pdf_path.name}: {exc}", file=sys.stderr)

    print(f"\n📚 Total: {grand_total} chunks en MongoDB '{args.collection}'")


if __name__ == "__main__":
    main()
