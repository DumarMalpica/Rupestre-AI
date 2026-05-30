from __future__ import annotations


def inpaint_image(image_path: str, mask_path: str | None) -> tuple[str, bool]:
    # ── MOCK ──
    # Reemplazar cuando DeepFillv2 esté entrenado:
    #   from models.deepfillv2.infer import load_deepfillv2
    #   model = load_deepfillv2("models/deepfillv2/weights.pth")
    #   result_array = model(image_array, mask_array)
    #   cv2.imwrite(output_path, result_array)
    #   return output_path, True
    if mask_path is None:
        return image_path, False
    return image_path, False
