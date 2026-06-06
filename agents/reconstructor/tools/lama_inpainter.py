from __future__ import annotations

import os
from pathlib import Path

import cv2
import numpy as np

from core.config import settings
from core.logger import get_logger

logger = get_logger("lama_inpainter")


class LaMaInpainter:
    _instance: LaMaInpainter | None = None
    _model: object | None = None

    def __new__(cls) -> LaMaInpainter:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self):
        if self._model is not None:
            return self._model
        try:
            from lama_cleaner.model.lama import LaMa as LaMaModel
        except ImportError:
            raise ImportError(
                "lama-cleaner no está instalado. Ejecuta:\n"
                "  pip install lama-cleaner --no-deps\n"
                "  pip install loguru yacs omegaconf einops timm scikit-image"
            )
        try:
            self._model = LaMaModel(device=settings.lama_device)
            logger.info(f"LaMa model loaded on {settings.lama_device}")
            return self._model
        except Exception as exc:
            logger.error(f"Failed to load LaMa model: {exc}")
            raise

    def _make_config(self):
        from lama_cleaner.schema import Config

        return Config(
            ldm_steps=1,
            ldm_sampler="plms",
            zits_wireframe=True,
            hd_strategy="original",
            hd_strategy_crop_margin=32,
            hd_strategy_crop_trigger_size=800,
            hd_strategy_resize_limit=800,
            prompt="",
            negative_prompt="",
            use_croper=False,
            croper_x=0,
            croper_y=0,
            croper_height=0,
            croper_width=0,
        )

    def inpaint(self, image_path: str, mask_path: str) -> str:
        model = self._load_model()

        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        if mask is None:
            raise ValueError(f"Could not read mask: {mask_path}")
        _, mask_binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

        cfg = self._make_config()
        result = model(image_rgb, mask_binary, cfg)

        os.makedirs(settings.output_dir, exist_ok=True)
        stem = Path(image_path).stem
        output_path = os.path.join(settings.output_dir, f"{stem}_lama.png")

        result_u8 = np.clip(np.array(result), 0, 255).astype(np.uint8)
        result_bgr = cv2.cvtColor(result_u8, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, result_bgr)

        logger.info(f"LaMa inpainting saved to {output_path}")
        return output_path


def inpaint_with_lama(image_path: str, mask_path: str | None) -> tuple[str, bool]:
    if not settings.lama_enabled:
        logger.info("LaMa is disabled via settings")
        return image_path, False
    if mask_path is None:
        logger.info("No mask provided, skipping LaMa")
        return image_path, False
    try:
        painter = LaMaInpainter()
        result_path = painter.inpaint(image_path, mask_path)
        return result_path, True
    except Exception as exc:
        logger.error(f"LaMa inpainting failed: {exc}")
        return image_path, False
