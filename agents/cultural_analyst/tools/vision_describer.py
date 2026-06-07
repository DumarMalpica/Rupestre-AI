from __future__ import annotations

import base64
import os

from core.config import settings
from core.logger import get_logger

logger = get_logger("cultural_analyst.vision")

_MOCK_DESCRIPTION = (
    "Pictograma con motivos en espiral y trazos lineales de pigmento rojizo "
    "sobre soporte rocoso. Se observan figuras geométricas concéntricas y "
    "posibles representaciones antropomorfas esquemáticas, con desgaste parcial "
    "por exposición a la intemperie."
)

_PROMPT = (
    "Eres un arqueólogo especialista en arte rupestre colombiano. "
    "Describe objetivamente este pictograma/petroglifo: motivos visibles "
    "(espirales, figuras antropomorfas o zoomorfas, líneas, puntos), técnica "
    "(pintura o grabado), color del pigmento, composición y estado de "
    "conservación. Sé conciso (máximo 150 palabras) y no especules sobre el "
    "significado cultural todavía."
)

_MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


def describe_image(image_path: str) -> str:
    """Genera una descripción visual del pictograma con Claude (visión).

    Cae a una descripción mock si el proveedor no es anthropic, falta la API
    key o la imagen no existe — el pipeline nunca se rompe.
    """
    if settings.llm_provider != "anthropic" or not settings.anthropic_api_key:
        return _MOCK_DESCRIPTION

    if not image_path or not os.path.exists(image_path):
        logger.warning(f"Imagen no encontrada: {image_path} — usando descripción mock")
        return _MOCK_DESCRIPTION

    try:
        import anthropic

        media_type = _MEDIA_TYPES.get(
            os.path.splitext(image_path)[1].lower(), "image/jpeg"
        )
        with open(image_path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model=settings.vision_model,
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": data,
                            },
                        },
                        {"type": "text", "text": _PROMPT},
                    ],
                }
            ],
        )
        text = next((b.text for b in response.content if b.type == "text"), "")
        return text.strip() or _MOCK_DESCRIPTION

    except Exception as exc:
        logger.warning(f"Descripción con Claude visión falló ({exc}) — usando mock")
        return _MOCK_DESCRIPTION
