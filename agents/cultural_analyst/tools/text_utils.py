from __future__ import annotations

# Mapeo directo: clases del modelo YOLO → términos arqueológicos ICANH
_YOLO_CLASS_MAP = {
    "Lines": "línea geométrica",
    "Person": "figura antropomorfa",
    "animal": "figura zoomorfa",
    "birds": "ave",
    "drawing": "motivo rupestre",
    "faces": "rostro",
    "figure": "figura antropomorfa",
    "fishs": "pez",
    "hands": "mano",
    "lizard": "lagarto",
    "monkey": "mono",
    "plants": "vegetal",
    "shield": "escudo",
    "sun": "figura solar",
}


def enrich_motifs(motifs: list[dict], description: str) -> list[dict]:
    """Traduce las clases de YOLO a términos arqueológicos usando _YOLO_CLASS_MAP.
    Si una clase no está en el mapa, se deja intacta.

    El parámetro `description` se conserva para compatibilidad pero ya no se usa.
    """
    if not motifs:
        return motifs

    enriched: list[dict] = []
    for motif in motifs:
        new_motif = dict(motif)
        clase_original = str(motif.get("clase", ""))
        new_motif["clase"] = _YOLO_CLASS_MAP.get(clase_original, clase_original)
        enriched.append(new_motif)
    return enriched
