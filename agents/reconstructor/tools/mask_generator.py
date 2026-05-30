from __future__ import annotations

import os
from pathlib import Path

import cv2
import numpy as np

from core.config import settings


def generate_mask(image_path: str) -> str | None:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None

    h, w = img.shape

    # Varianza local del Laplaciano en ventanas 16x16
    lap = cv2.Laplacian(img, cv2.CV_64F)
    lap_sq = np.float32(lap**2)
    local_var = cv2.boxFilter(lap_sq, ddepth=-1, ksize=(16, 16), normalize=True)

    # Zonas con varianza < 20 → posiblemente deterioradas
    _, mask = cv2.threshold(local_var, 20.0, 255.0, cv2.THRESH_BINARY_INV)
    mask = np.uint8(mask)

    # Morfología para limpiar ruido
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    mask_pixels = int(np.sum(mask > 0))
    if mask_pixels < h * w * 0.01:
        return None  # deterioro < 1% → no requiere reconstrucción

    os.makedirs(settings.output_dir, exist_ok=True)
    stem = Path(image_path).stem
    output_path = os.path.join(settings.output_dir, f"{stem}_mask.png")
    cv2.imwrite(output_path, mask)
    return output_path
