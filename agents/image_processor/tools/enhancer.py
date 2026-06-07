from __future__ import annotations

import os
from pathlib import Path

import cv2
import numpy as np

from core.config import settings


def _stretch_channel(channel: np.ndarray, target_std: float) -> np.ndarray:
    """Decorrelation stretch: amplifica las desviaciones respecto al gris.

    El pigmento rojo tenue (canal a* ligeramente > 128) se vuelve vívido sin
    cambiar su tono — el eje rojo-verde se estira, no se rota.
    """
    ch = channel.astype(np.float32)
    mean = float(ch.mean())
    std = float(ch.std()) + 1e-6
    stretched = (ch - mean) * (target_std / std) + mean
    return np.clip(stretched, 0, 255).astype(np.uint8)


def enhance_image(image_path: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)

    img = cv2.imread(image_path)
    if img is None:
        return image_path

    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    # Contraste local en luminancia
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l_channel)

    # Realce del rojo (estilo DStretch): estira solo el eje rojo-verde (a*).
    # El eje azul-amarillo (b*) se deja intacto para no introducir azules.
    a_enhanced = _stretch_channel(a_channel, settings.dstretch_red_std)

    lab_enhanced = cv2.merge((l_enhanced, a_enhanced, b_channel))
    enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

    stem = Path(image_path).stem
    output_path = os.path.join(output_dir, f"{stem}_enhanced.jpg")
    cv2.imwrite(output_path, enhanced)

    return output_path
