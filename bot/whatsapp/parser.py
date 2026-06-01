from __future__ import annotations

import re


def parse_coordinates(text: str) -> tuple[float, float] | None:
    """
    Acepta múltiples formatos:
      5.634, -73.525
      5.634°N, 73.525°W
      5.634 -73.525
      lat:5.634 lon:-73.525

    Retorna (lat, lon) o None si no puede parsear.
    """
    normalized = (
        text.replace("°N", "")
        .replace("°W", " -")
        .replace("°S", " -")
        .replace("°E", "")
        .replace("lat:", "")
        .replace("lon:", "")
        .replace("N", "")
        .replace("W", "-")
    )

    numbers = re.findall(r"-?\d+\.?\d*", normalized)
    if len(numbers) >= 2:
        try:
            lat = float(numbers[0])
            lon = float(numbers[1])
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon
        except ValueError:
            pass
    return None


def parse_municipality_department(text: str) -> tuple[str, str]:
    """
    Acepta: 'Villa de Leyva, Boyacá' o 'Villa de Leyva - Boyacá'
    Retorna (municipio, departamento).
    Si no encuentra separador, retorna (text, 'No especificado').
    """
    for sep in [",", "-", "/"]:
        if sep in text:
            parts = text.split(sep, 1)
            return parts[0].strip().title(), parts[1].strip().title()
    return text.strip().title(), "No especificado"
