from __future__ import annotations

import os
from pathlib import Path

import cv2


def enhance_image(image_path: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)

    img = cv2.imread(image_path)

    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l_channel)

    lab_enhanced = cv2.merge((l_enhanced, a_channel, b_channel))
    enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

    stem = Path(image_path).stem
    output_path = os.path.join(output_dir, f"{stem}_enhanced.jpg")
    cv2.imwrite(output_path, enhanced)

    return output_path
