from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Form

from bot.whatsapp.handler import handle_message

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


@router.post("/webhook")
async def whatsapp_webhook(
    background_tasks: BackgroundTasks,
    From: str = Form(...),
    Body: str = Form(""),
    NumMedia: int = Form(0),
    MediaUrl0: Optional[str] = Form(None),
    MediaContentType0: Optional[str] = Form(None),
) -> dict:
    """
    Twilio envía un POST a este endpoint por cada mensaje de WhatsApp entrante.
    Respondemos 200 de inmediato y procesamos el mensaje en background,
    evitando que Twilio reintente por timeout (límite: 15 s).
    """
    background_tasks.add_task(
        handle_message,
        phone=From,
        body=Body,
        media_url=MediaUrl0,
        media_type=MediaContentType0,
        num_media=NumMedia,
    )
    return {"status": "ok"}
