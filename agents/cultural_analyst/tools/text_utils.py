from __future__ import annotations

# Etiquetas genéricas que el modelo YOLO suele asignar (p.ej. "Drawing") y que
# conviene reemplazar por un término arqueológico inferido de la descripción.
_GENERIC = {
    "drawing",
    "draw",
    "unknown",
    "desconocido",
    "objeto",
    "object",
    "motivo",
    "figura",
    "sin clase",
    "na",
    "",
}

# Palabras clave en la descripción visual → etiqueta canónica del motivo.
# El orden importa: la primera coincidencia define la etiqueta.
_KEYWORDS: list[tuple[tuple[str, ...], str]] = [
    (
        (
            "persona",
            "humano",
            "humana",
            "antropomorf",
            "figura humana",
            "hombre",
            "mujer",
            "chamán",
            "chaman",
        ),
        "figura antropomorfa",
    ),
    (
        (
            "zoomorf",
            "animal",
            "cuadrúpedo",
            "cuadrupedo",
            "ave",
            "pájaro",
            "pajaro",
            "serpiente",
            "rana",
            "felino",
            "venado",
            "lagarto",
        ),
        "figura zoomorfa",
    ),
    (("espiral",), "espiral"),
    (("solar", "sol ", "rayos", "concéntric", "concentric"), "figura solar"),
    (
        ("geométric", "geometric", "línea", "linea", "zigzag", "reticul", "trazo"),
        "línea geométrica",
    ),
    (("cúpula", "cupula", "cazoleta", "punto"), "punto cúpula"),
    (("mano", "manos"), "mano"),
]


def _labels_from_description(description: str) -> list[str]:
    desc = (description or "").lower()
    found: list[str] = []
    for keywords, label in _KEYWORDS:
        if any(kw in desc for kw in keywords) and label not in found:
            found.append(label)
    return found


def enrich_motifs(motifs: list[dict], description: str) -> list[dict]:
    """Reetiqueta motivos genéricos (p.ej. "Drawing") con términos inferidos
    de la descripción visual (p.ej. "figura antropomorfa" si menciona persona).

    Los motivos ya etiquetados con una clase específica se dejan intactos.
    """
    if not motifs:
        return motifs

    found = _labels_from_description(description)
    if not found:
        return motifs

    enriched: list[dict] = []
    generic_idx = 0
    for motif in motifs:
        clase = str(motif.get("clase", "")).strip().lower().replace("_", " ")
        new_motif = dict(motif)
        if clase in _GENERIC:
            new_motif["clase"] = found[generic_idx % len(found)]
            generic_idx += 1
        enriched.append(new_motif)
    return enriched
