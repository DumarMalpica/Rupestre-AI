from __future__ import annotations

import os

from twilio.rest import Client


def _client() -> Client:
    return Client(
        os.getenv("TWILIO_ACCOUNT_SID"),
        os.getenv("TWILIO_AUTH_TOKEN"),
    )


def send_message(to: str, body: str) -> None:
    """Envía un mensaje de texto por WhatsApp."""
    _client().messages.create(
        from_=os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886"),
        to=to,
        body=body,
    )


def send_document(to: str, railway_url: str, record_id: str) -> None:
    """
    WhatsApp Sandbox no permite enviar archivos binarios salientes,
    así que enviamos el enlace de descarga de la API.
    """
    download_url = f"{railway_url}/api/records/{record_id}/pdf"
    send_message(
        to,
        (
            f"✅ *Ficha ICANH generada*\n\n"
            f"📄 Descarga tu ficha:\n{download_url}\n\n"
            f"🔑 Record ID: `{record_id}`"
        ),
    )
