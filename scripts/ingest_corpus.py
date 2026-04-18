"""
Pipeline de ingesta del corpus ICANH/UPTC.
Uso: python scripts/ingest_corpus.py --source ./data/icanh_docs/
"""

import argparse
from corpus.ingest.pdf_loader import load_directory
from corpus.processing.chunker import chunk_documents
from corpus.vectorstore.indexer import index_chunks
from core.logger import get_logger

logger = get_logger("scripts.ingest")


def main():
    parser = argparse.ArgumentParser(description="Ingesta del corpus rupestre")
    parser.add_argument("--source", default="./data/icanh_docs/")
    args = parser.parse_args()

    print(f"\n📚 Iniciando ingesta desde: {args.source}")

    # 1. Cargar documentos
    docs = load_directory(args.source)
    print(f"   {len(docs)} páginas cargadas")

    # 2. Segmentar en chunks
    chunks = chunk_documents(docs)
    print(f"   {len(chunks)} chunks generados")

    # 3. Indexar en ChromaDB
    indexed = index_chunks(chunks)
    print(f"   {indexed} chunks indexados exitosamente")
    print("\n✅ Ingesta completada")


if __name__ == "__main__":
    main()
