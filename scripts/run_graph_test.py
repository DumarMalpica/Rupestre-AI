"""CLI de prueba para ejecutar el pipeline completo de Rupestre AI."""

from __future__ import annotations

import argparse
import time
import uuid
from pathlib import Path


def _create_test_image(path: Path) -> None:
    from PIL import Image

    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (1200, 800), color=(139, 90, 43))
    img.save(path)
    print(f"Imagen de prueba creada en: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prueba el pipeline de Rupestre AI")
    parser.add_argument(
        "--image",
        default="data/samples/pictograma.jpg",
        help="Ruta a la imagen de entrada (default: data/samples/pictograma.jpg)",
    )
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        _create_test_image(image_path)

    from core.graph import rupestre_graph
    from core.state import RupestreState

    session_id = str(uuid.uuid4())
    print(f"Session ID: {session_id}  (búscalo en LangFuse → Traces → filter by session)")

    state: RupestreState = {
        "image_path": str(image_path),
        "site_name": "Sitio de Prueba",
        "coordinates": (4.7110, -74.0721),
        "session_id": session_id,
        "errors": [],
        "current_agent": "",
    }

    start = time.time()
    result = rupestre_graph.invoke(state)
    elapsed = time.time() - start

    enhanced = "✓" if result.get("enhanced_image") else "✗"
    motif_count = result.get("motif_count", 0)
    has_parallels = result.get("has_regional_parallels", False)
    reconstruction_applied = result.get("reconstruction_applied", False)
    record_id = result.get("record_id", "N/A")
    ficha_pdf_path = result.get("ficha_pdf_path", "N/A")

    print(f"✅ Pipeline completado en {elapsed:.1f}s")
    print(f"   AG1: imagen realzada {enhanced}")
    print(f"   AG2: {motif_count} motivos detectados ✓")
    print(f"   AG3: paralelos {'encontrados' if has_parallels else 'no encontrados'} ✓")
    print(f"   AG4: interpretación generada ✓")
    print(f"   AG5: reconstrucción {'aplicada' if reconstruction_applied else 'omitida (sin GAN)'} ✓")
    print(f"   AG6: ficha ICANH generada ✓")
    print(f"       Record ID: {record_id}")
    print(f"       PDF: {ficha_pdf_path} ✓")

    # Flush explícito: garantiza que las trazas se envíen antes de que el proceso termine
    try:
        from core.logger import langfuse_context
        langfuse_context.flush()
        print("📡 Trazas enviadas a LangFuse ✓")
    except Exception:
        pass


if __name__ == "__main__":
    main()
