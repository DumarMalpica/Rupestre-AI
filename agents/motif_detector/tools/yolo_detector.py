from __future__ import annotations

import os
from typing import Any

from ultralytics import YOLO

_model = None
_model_path = os.path.join("models", "yolov11", "yolo11_v3_map_final.pt")

# Mapeo determinista de las clases del modelo YOLO (inglés) a la etiqueta
# arqueológica en español que se muestra en la ficha. La clave se compara en
# minúsculas. Las clases genéricas (drawing/figure) caen a "Motivo sin
# clasificar" en lugar de inventar un tipo.
_CLASS_LABELS = {
    "person": "Figura antropomorfa",
    "animal": "Figura zoomorfa",
    "birds": "Ave",
    "fishs": "Pez",
    "lizard": "Lagarto",
    "monkey": "Mono",
    "hands": "Manos",
    "faces": "Rostros",
    "plants": "Planta",
    "shield": "Escudo / geométrico",
    "sun": "Figura solar",
    "lines": "Línea geométrica",
    "drawing": "Motivo rupestre",
    "figure": "Figura antropomorfa",
}

# Taxonomía canónica para clasificación: las clases del modelo YOLO (en español,
# sin duplicar las dos genéricas). Fuente única de verdad que reusa el
# clasificador por visión para etiquetar cada figura en uno de estos tipos.
MOTIF_CLASSES = [
    "Figura antropomorfa",
    "Figura zoomorfa",
    "Ave",
    "Pez",
    "Lagarto",
    "Mono",
    "Manos",
    "Rostros",
    "Planta",
    "Escudo / geométrico",
    "Figura solar",
    "Línea geométrica",
    "Motivo sin clasificar",
]


def _get_model() -> YOLO:
    global _model
    if _model is None:
        if not os.path.exists(_model_path):
            raise FileNotFoundError(
                f"No se encontró el archivo del modelo YOLOv11 en: {_model_path}"
            )
        _model = YOLO(_model_path)
    return _model


def detect_motifs(
    image_path: str, confidence_threshold: float = 0.5
) -> list[dict[str, Any]]:
    if not image_path or not os.path.exists(image_path):
        return []

    model = _get_model()
    results = model(image_path, conf=confidence_threshold)

    motifs: list[dict[str, Any]] = []
    for result in results:
        boxes = result.boxes
        for i, box in enumerate(boxes):
            # Coordenadas [x1, y1, x2, y2]
            xyxy = box.xyxy[0].tolist()
            x1, y1, x2, y2 = [int(val) for val in xyxy]

            # Confianza
            conf = float(box.conf[0])

            # Nombre de la clase detectada (traducido a etiqueta en español)
            cls_id = int(box.cls[0])
            raw_class = model.names.get(cls_id, f"class_{cls_id}")
            class_name = _CLASS_LABELS.get(raw_class.lower(), raw_class)

            motifs.append(
                {
                    "id": f"motif_{len(motifs) + 1:03d}",
                    "clase": class_name,
                    "confidence": conf,
                    "bbox": [x1, y1, x2, y2],
                    "crop_path": None,
                    "mask": None,
                }
            )
    return motifs
