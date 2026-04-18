"""
Prueba rápida del grafo completo con una imagen de muestra.
Uso: python scripts/run_graph_test.py --image data/samples/test.jpg
"""

import argparse
import json
import time
from core.graph import rupestre_graph

def main():
    parser = argparse.ArgumentParser(description="Test del grafo LangGraph")
    parser.add_argument("--image", default="data/samples/test_pictogram.jpg")
    parser.add_argument("--site", default="Villa de Leyva - Test")
    args = parser.parse_args()

    initial_state = {
        "image_path": args.image,
        "site_name": args.site,
        "coordinates": (5.634, -73.525),
        "session_id": "test-run-001",
        "errors": [],
    }

    print("\n🪨 Rupestre AI — Test del Grafo")
    print(f"   Imagen: {args.image}")
    print(f"   Sitio:  {args.site}")
    print("-" * 50)

    start = time.time()
    result = rupestre_graph.invoke(initial_state)
    elapsed = time.time() - start

    print(f"\n✅ Pipeline completado en {elapsed:.1f}s")
    print(f"   Agente final: {result.get('current_agent')}")
    print(f"   Motivos: {result.get('motif_count', 0)}")
    print(f"   Paralelos regionales: {result.get('has_regional_parallels')}")
    print(f"   Reconstrucción aplicada: {result.get('reconstruction_applied')}")
    print(f"   Record ID: {result.get('record_id')}")

    if result.get("ficha_json"):
        print("\n📋 Ficha JSON:")
        print(json.dumps(result["ficha_json"], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
