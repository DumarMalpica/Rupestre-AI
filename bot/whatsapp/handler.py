from __future__ import annotations

import asyncio
import os
import uuid

from bot.whatsapp.conversation import ConversationSession, get_session, reset_session
from bot.whatsapp.downloader import download_whatsapp_image
from bot.whatsapp.parser import parse_coordinates, parse_municipality_department
from bot.whatsapp.responder import send_document, send_message
from core.graph import rupestre_graph
from core.logger import get_logger

logger = get_logger("whatsapp_handler")

MSGS = {
    "welcome": (
        "🪨 *Bienvenido a Rupestre AI*\n"
        "Sistema de documentación de arte rupestre precolombino — UPTC\n\n"
        "📸 Envía una *foto del pictograma* para comenzar el análisis."
    ),
    "ask_site": (
        "✅ Foto recibida.\n\n"
        "📍 ¿Cuál es el *nombre del sitio* rupestre?\n"
        "_Ejemplo: Piedras del Tunjo, Cerro de los Muertos_"
    ),
    "ask_municipality": (
        "📍 ¿En qué *municipio y departamento* se encuentra?\n"
        "_Ejemplo: Villa de Leyva, Boyacá_"
    ),
    "ask_coordinates": (
        "🌐 ¿Cuáles son las *coordenadas GPS* del sitio?\n"
        "_Comparte tu ubicación 📍 o escríbelas:_\n"
        "_Ejemplo: 5.634, -73.525_"
    ),
    "processing": (
        "⏳ *Procesando análisis...*\n\n"
        "El pipeline está analizando el pictograma:\n"
        "• AG1: Realzando imagen\n"
        "• AG2: Detectando motivos\n"
        "• AG3: Comparando con inventario\n"
        "• AG4: Generando interpretación cultural\n"
        "• AG6: Generando ficha ICANH\n\n"
        "_Esto puede tardar hasta 60 segundos._"
    ),
    "error": (
        "❌ Ocurrió un error al procesar la imagen.\n"
        "Envía *reiniciar* para intentarlo de nuevo."
    ),
    "bad_coords": (
        "⚠️ No pude leer las coordenadas.\n"
        "Por favor escríbelas así: *5.634, -73.525*\n"
        "O comparte tu ubicación directamente 📍"
    ),
}

_RESET_CMDS = {"reiniciar", "reset", "restart", "hola", "start", "hi"}


async def handle_message(
    phone: str,
    body: str,
    media_url: str | None,
    media_type: str | None,
    num_media: int,
) -> None:
    """
    Procesa cada mensaje entrante de WhatsApp.
    `phone` incluye el prefijo 'whatsapp:+57...'
    Se ejecuta como BackgroundTask — la respuesta HTTP ya fue enviada a Twilio.
    """
    body_clean = (body or "").strip()
    body_lower = body_clean.lower()
    session = get_session(phone)

    # Comando de reinicio disponible en cualquier estado
    if body_lower in _RESET_CMDS:
        reset_session(phone)
        send_message(phone, MSGS["welcome"])
        return

    # ── WAITING_PHOTO ─────────────────────────────────────────────────────────
    if session.state == "WAITING_PHOTO":
        if num_media > 0 and media_url and "image" in (media_type or ""):
            send_message(phone, "⏳ Descargando imagen...")
            try:
                path = download_whatsapp_image(
                    media_url,
                    os.getenv("TWILIO_ACCOUNT_SID", ""),
                    os.getenv("TWILIO_AUTH_TOKEN", ""),
                )
                session.image_path = path
                session.state = "WAITING_SITE_NAME"
                send_message(phone, MSGS["ask_site"])
            except Exception as exc:
                logger.error(f"Error descargando imagen: {exc}")
                send_message(phone, "❌ No pude descargar la imagen. Intenta enviarla de nuevo.")
        else:
            send_message(phone, MSGS["welcome"])
        return

    # ── WAITING_SITE_NAME ─────────────────────────────────────────────────────
    if session.state == "WAITING_SITE_NAME":
        if len(body_clean) < 3:
            send_message(phone, "Por favor escribe el nombre del sitio (mínimo 3 caracteres).")
            return
        session.site_name = body_clean.title()
        session.state = "WAITING_MUNICIPALITY"
        send_message(phone, MSGS["ask_municipality"])
        return

    # ── WAITING_MUNICIPALITY ──────────────────────────────────────────────────
    if session.state == "WAITING_MUNICIPALITY":
        municipality, department = parse_municipality_department(body_clean)
        session.municipality = municipality
        session.department = department
        session.state = "WAITING_COORDINATES"
        send_message(phone, MSGS["ask_coordinates"])
        return

    # ── WAITING_COORDINATES ───────────────────────────────────────────────────
    if session.state == "WAITING_COORDINATES":
        coords = parse_coordinates(body_lower)
        if coords is None:
            send_message(phone, MSGS["bad_coords"])
            return

        session.latitude, session.longitude = coords
        session.state = "PROCESSING"

        # send_message es sync → el usuario recibe "Procesando..." inmediatamente
        send_message(phone, MSGS["processing"])

        # Pipeline LangGraph (sync) en executor para no bloquear el event loop
        await _run_pipeline(phone, session)
        return

    # ── PROCESSING ────────────────────────────────────────────────────────────
    if session.state == "PROCESSING":
        send_message(phone, "⏳ Tu análisis ya está en proceso, por favor espera...")
        return

    # ── DONE ──────────────────────────────────────────────────────────────────
    if session.state == "DONE":
        send_message(
            phone,
            "✅ Tu ficha ya fue generada. Envía *reiniciar* para analizar otro pictograma.",
        )
        return


async def _run_pipeline(phone: str, session: ConversationSession) -> None:
    """Ejecuta el grafo LangGraph y envía el resultado al usuario."""
    railway_url = os.getenv("RAILWAY_PUBLIC_DOMAIN", "http://localhost:8000")
    if not railway_url.startswith("http"):
        railway_url = f"https://{railway_url}"

    try:
        state = {
            "image_path": session.image_path,
            "site_name": session.site_name,
            "coordinates": (session.latitude, session.longitude),
            "session_id": str(uuid.uuid4()),
            "errors": [],
            "current_agent": "",
        }

        # rupestre_graph.invoke es síncrono — lo ejecutamos en un thread pool
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, rupestre_graph.invoke, state)

        record_id = result.get("record_id", "N/A")
        motif_count = result.get("motif_count", 0)
        confidence = result.get("interpretation_confidence", 0.0)
        requires_hitl = result.get("requires_human_review", False)

        summary = (
            f"🪨 *Análisis completado*\n\n"
            f"📍 Sitio: {session.site_name}\n"
            f"🗺️ {session.municipality}, {session.department}\n"
            f"🔍 Motivos detectados: *{motif_count}*\n"
            f"📊 Confianza RAG: *{confidence:.0%}*\n"
        )
        if requires_hitl:
            summary += "\n⚠️ _Requiere revisión por arqueólogo experto._"

        send_message(phone, summary)
        send_document(phone, railway_url, record_id)

        session.state = "DONE"

    except Exception as exc:
        logger.error(f"Error en pipeline WhatsApp [{phone}]: {exc}")
        send_message(phone, MSGS["error"])
        session.state = "WAITING_PHOTO"
