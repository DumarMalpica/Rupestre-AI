from __future__ import annotations

import cv2
import numpy as np

from core.config import settings


def check_quality(image_path: str) -> tuple[bool, str]:
    import os

    if not os.path.exists(image_path):
        return False, "Archivo no encontrado"

    img = cv2.imread(image_path)
    if img is None:
        return False, "No se pudo leer la imagen"

    h, w = img.shape[:2]
    if h * w < settings.min_image_resolution:
        return False, f"Resolución insuficiente: {w}x{h}"

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    if variance < settings.blur_threshold:
        return False, f"Imagen desenfocada: varianza={variance:.1f}"

    if np.mean(img) > 240:
        return False, "Imagen sobreexpuesta"

    return True, "OK"
