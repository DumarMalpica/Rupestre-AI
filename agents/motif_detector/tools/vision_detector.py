"""Detección de motivos por visión (Claude) sobre la imagen completa.

El modelo YOLO localiza pocas figuras (suele perder el antropomorfo central,
manos, etc.) y colapsa casi todo a "drawing". Este detector le pide a Claude que
enumere TODAS las figuras distinguibles del pictograma, cada una con su tipo
(taxonomía de `MOTIF_CLASSES`), su caja aproximada y una confianza.

Se usa como detector primario cuando hay proveedor anthropic; si no, el agente
cae a YOLO. Devuelve [] ante cualquier fallo para no romper el pipeline.
"""

from __future__ import annotations

import base64
import json
import os
import re

from agents.motif_detector.tools.yolo_detector import MOTIF_CLASSES
from core.config import settings
from core.logger import get_logger

logger = get_logger("motif_detector.vision_detector")

_MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


def _build_prompt(width: int, height: int) -> str:
    return (
        "Eres un arqueólogo especialista en arte rupestre colombiano. Analiza "
        "este pictograma/petroglifo e identifica TODAS las figuras o motivos "
        f"individuales distinguibles. La imagen mide {width}x{height} píxeles "
        "(origen 0,0 arriba-izquierda).\n\n"
        "Clasifica CADA figura en exactamente UNO de estos tipos:\n"
        + ", ".join(MOTIF_CLASSES)
        + ".\n\nDevuelve SOLO un arreglo JSON; cada elemento con: "
        '"tipo" (uno de la lista), "bbox" ([x1,y1,x2,y2] en píxeles que encierran '
        'la figura) y "confianza" (0.0-1.0 según qué tan claro es el motivo). '
        'Ejemplo: [{"tipo":"Figura antropomorfa","bbox":[120,80,260,400],'
        '"confianza":0.9}]. No incluyas texto fuera del JSON. Enumera cada figura '
        "por separado aunque se repita el tipo; usa \"Motivo sin clasificar\" solo "
        "si una figura es realmente irreconocible."
    )


def _parse_array(text: str) -> list:
    try:
        data = json.loads(text)
        return data if isinstance(data, list) else []
    except Exception:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                return data if isinstance(data, list) else []
            except Exception:
                return []
    return []


def detect_motifs_vision(image_path: str) -> list[dict]:
    """Enumera las figuras del pictograma con Claude. [] si no aplica o falla."""
    if settings.llm_provider != "anthropic" or not settings.anthropic_api_key:
        return []
    if not image_path or not os.path.exists(image_path):
        return []

    try:
        import anthropic
        from PIL import Image

        with Image.open(image_path) as im:
            width, height = im.size

        media_type = _MEDIA_TYPES.get(
            os.path.splitext(image_path)[1].lower(), "image/jpeg"
        )
        with open(image_path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model=settings.vision_model,
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": data,
                            },
                        },
                        {"type": "text", "text": _build_prompt(width, height)},
                    ],
                }
            ],
        )
        text = next((b.text for b in response.content if b.type == "text"), "")
        items = _parse_array(text)[: settings.motif_max_classify]

        valid = {label.lower(): label for label in MOTIF_CLASSES}
        motifs: list[dict] = []
        for item in items:
            tipo = str(item.get("tipo", "")).strip().lower()
            clase = valid.get(tipo, "Motivo sin clasificar")
            bbox = item.get("bbox") or [0, 0, 0, 0]
            try:
                x1, y1, x2, y2 = (int(v) for v in bbox)
            except Exception:
                x1, y1, x2, y2 = 0, 0, 0, 0
            try:
                conf = float(item.get("confianza", 0.0))
            except Exception:
                conf = 0.0
            motifs.append(
                {
                    "id": f"motif_{len(motifs) + 1:03d}",
                    "clase": clase,
                    "confidence": max(0.0, min(1.0, conf)),
                    "bbox": [x1, y1, x2, y2],
                    "crop_path": None,
                    "mask": None,
                }
            )

        logger.info(f"Detección por visión: {len(motifs)} figuras enumeradas")
        return motifs

    except Exception as exc:
        logger.warning(f"Detección por visión falló ({exc}) — se usará YOLO")
        return []
