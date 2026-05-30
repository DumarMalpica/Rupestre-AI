from __future__ import annotations


def detect_motifs(
    image_path: str, confidence_threshold: float = 0.5
) -> list[dict]:
    # ── MOCK ──
    # Reemplazar cuando el modelo YOLOv11 esté entrenado:
    #   from ultralytics import YOLO
    #   model = YOLO("models/yolov11/weights.pt")
    #   results = model(image_path, conf=confidence_threshold)
    return [
        {
            "id": "motif_001",
            "clase": "espiral",
            "confidence": 0.91,
            "bbox": [120, 80, 340, 290],
            "crop_path": None,
            "mask": None,
        },
        {
            "id": "motif_002",
            "clase": "figura_antropomorfa",
            "confidence": 0.78,
            "bbox": [400, 150, 580, 380],
            "crop_path": None,
            "mask": None,
        },
    ]
