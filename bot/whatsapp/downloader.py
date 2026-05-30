from __future__ import annotations

import os
import uuid

import httpx

from core.config import settings


def download_whatsapp_image(
    media_url: str,
    account_sid: str,
    auth_token: str,
) -> str:
    """
    Descarga la imagen enviada por WhatsApp vía Twilio.
    Retorna la ruta local donde fue guardada.
    """
    os.makedirs(settings.samples_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex[:8]}_pictograma.jpg"
    output_path = os.path.join(settings.samples_dir, filename)

    with httpx.Client(timeout=30) as client:
        response = client.get(
            media_url,
            auth=(account_sid, auth_token),
            follow_redirects=True,
        )
        response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)

    return output_path
