from __future__ import annotations

import os

from ultralytics import YOLO

_model = None
_model_path = os.path.join("models", "yolov11", "yolo11_v3_map_final.pt")


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
) -> list[dict]:
    model = _get_model()
    results = model(image_path, conf=confidence_threshold)

    motifs = []
    for result in results:
        boxes = result.boxes
        for i, box in enumerate(boxes):
            # Coordenadas [x1, y1, x2, y2]
            xyxy = box.xyxy[0].tolist()
            x1, y1, x2, y2 = [int(val) for val in xyxy]

            # Confianza
            conf = float(box.conf[0])

            # Nombre de la clase detectada
            cls_id = int(box.cls[0])
            class_name = model.names.get(cls_id, f"class_{cls_id}")

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

