from __future__ import annotations

import os
from pathlib import Path

import cv2


def annotate_image(image_path: str, motifs: list[dict], output_dir: str) -> str:
    if not motifs or not os.path.exists(image_path):
        return image_path

    img = cv2.imread(image_path)
    if img is None:
        return image_path

    for motif in motifs:
        x1, y1, x2, y2 = motif["bbox"]
        cv2.rectangle(img, (x1, y1), (x2, y2), color=(0, 255, 0), thickness=2)

        label = f"{motif['clase']} {motif['confidence']:.2f}"
        cv2.putText(
            img,
            label,
            (x1, max(y1 - 6, 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.55,
            color=(0, 255, 0),
            thickness=1,
            lineType=cv2.LINE_AA,
        )

    os.makedirs(output_dir, exist_ok=True)
    stem = Path(image_path).stem
    output_path = os.path.join(output_dir, f"{stem}_annotated.jpg")
    cv2.imwrite(output_path, img)
    return output_path
