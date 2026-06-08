"""Clasificación de figuras detectadas usando Claude visión.

YOLO localiza las figuras (cajas) pero el modelo actual colapsa casi todo a la
clase genérica "drawing". Este módulo recorta cada figura genérica y le pide a
Claude que la clasifique en una taxonomía cerrada de motivos rupestres. A
diferencia del antiguo `enrich_motifs` (que adivinaba en ronda desde una sola
descripción global), aquí cada etiqueta se basa en el recorte de esa figura.

Cae con gracia (deja las etiquetas intactas) si el proveedor no es anthropic,
falta la API key, o la imagen no existe — el pipeline nunca se rompe.
"""

from __future__ import annotations

import base64
import io
import json
import os
import re

from agents.motif_detector.tools.yolo_detector import MOTIF_CLASSES
from core.config import settings
from core.logger import get_logger

logger = get_logger("motif_detector.vision_classifier")

# Taxonomía cerrada = las clases del propio modelo YOLO (fuente única en
# yolo_detector.MOTIF_CLASSES). Claude debe elegir exactamente una por figura.
_TAXONOMY = MOTIF_CLASSES

# Etiquetas que se consideran genéricas y por tanto se reclasifican. Las figuras
# que YOLO ya etiquetó con una clase específica se conservan.
_GENERIC = {"motivo sin clasificar", "drawing", "draw", "figure", "objeto", ""}

_PROMPT = (
    "Eres un arqueólogo especialista en arte rupestre colombiano. Te muestro "
    "recortes de figuras individuales detectadas en un pictograma/petroglifo, "
    "numeradas desde 0. Clasifica CADA figura en exactamente UNA de estas "
    "categorías:\n"
    + ", ".join(_TAXONOMY)
    + ".\n\nResponde SOLO con un objeto JSON que mapee el índice de cada figura "
    'a su categoría. Ejemplo: {"0": "Figura antropomorfa", "1": "Espiral"}. '
    'Si una figura es ambigua o no reconocible, usa "Motivo sin clasificar".'
)


def _crop_to_b64(image, box: list[int], pad_frac: float = 0.08) -> str:
    """Recorta la caja (con un margen) y la devuelve como JPEG base64."""
    x1, y1, x2, y2 = box
    w, h = image.size
    pw = int((x2 - x1) * pad_frac)
    ph = int((y2 - y1) * pad_frac)
    crop = image.crop(
        (max(0, x1 - pw), max(0, y1 - ph), min(w, x2 + pw), min(h, y2 + ph))
    )
    buf = io.BytesIO()
    crop.convert("RGB").save(buf, format="JPEG", quality=85)
    return base64.standard_b64encode(buf.getvalue()).decode("utf-8")


def _parse_mapping(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                return {}
    return {}


def classify_motifs(image_path: str, motifs: list[dict]) -> list[dict]:
    """Reetiqueta las figuras genéricas clasificando su recorte con Claude.

    Conserva las figuras que YOLO ya etiquetó con una clase específica.
    """
    if not motifs:
        return motifs
    if settings.llm_provider != "anthropic" or not settings.anthropic_api_key:
        return motifs
    if not image_path or not os.path.exists(image_path):
        return motifs

    targets = [
        i
        for i, m in enumerate(motifs)
        if str(m.get("clase", "")).strip().lower() in _GENERIC
    ][: settings.motif_max_classify]
    if not targets:
        return motifs

    try:
        import anthropic
        from PIL import Image

        img = Image.open(image_path)
        content: list[dict] = [{"type": "text", "text": _PROMPT}]
        for local_idx, motif_idx in enumerate(targets):
            content.append({"type": "text", "text": f"Figura {local_idx}:"})
            content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": _crop_to_b64(img, motifs[motif_idx]["bbox"]),
                    },
                }
            )

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model=settings.vision_model,
            max_tokens=512,
            messages=[{"role": "user", "content": content}],
        )
        text = next((b.text for b in response.content if b.type == "text"), "")
        mapping = _parse_mapping(text)

        valid = {label.lower(): label for label in _TAXONOMY}
        relabeled = 0
        for local_idx, motif_idx in enumerate(targets):
            raw = str(mapping.get(str(local_idx), "")).strip().lower()
            if raw in valid:
                motifs[motif_idx] = {**motifs[motif_idx], "clase": valid[raw]}
                relabeled += 1

        logger.info(
            f"Clasificación visión: {relabeled}/{len(targets)} figuras reetiquetadas"
        )
    except Exception as exc:
        logger.warning(f"Clasificación visión falló ({exc}) — etiquetas sin cambio")

    return motifs
