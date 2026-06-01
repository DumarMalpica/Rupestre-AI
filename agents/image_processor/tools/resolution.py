from __future__ import annotations

import math
import os
from pathlib import Path

import cv2


def maybe_upscale_to_min_resolution(
    image_path: str,
    output_dir: str,
    *,
    min_area: int,
    max_upscale_factor: float,
) -> tuple[str, bool]:
    """
    Up-scales the image (keeping aspect ratio) until it reaches `min_area`.

    Returns (path, was_upscaled). If the required upscale factor exceeds
    `max_upscale_factor`, it does nothing and returns the original path.
    """
    if not image_path or not os.path.exists(image_path):
        return image_path, False

    img = cv2.imread(image_path)
    if img is None:
        return image_path, False

    h, w = img.shape[:2]
    current_area = h * w
    if current_area >= min_area:
        return image_path, False

    # Scale factor needed for area to reach `min_area`.
    scale = math.sqrt(min_area / float(current_area))
    if scale > max_upscale_factor:
        return image_path, False

    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))

    upscaled = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    os.makedirs(output_dir, exist_ok=True)

    stem = Path(image_path).stem
    out_path = os.path.join(output_dir, f"{stem}_upscaled_{new_w}x{new_h}.jpg")
    ok = cv2.imwrite(out_path, upscaled)
    if not ok:
        return image_path, False
    return out_path, True

