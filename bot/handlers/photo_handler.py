"""Maneja la recepción de fotografías del sitio rupestre."""

import httpx
from aiogram import Router, F
from aiogram.types import Message, PhotoSize
from aiogram.fsm.context import FSMContext
from bot.fsm.states import AnalysisFlow
from core.config import settings
from core.logger import get_logger

logger = get_logger("bot.photo_handler")
router = Router()

API_URL = f"http://{settings.api_host}:{settings.api_port}"


@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """Usuario envía una fotografía → pedir nombre del sitio."""
    photo: PhotoSize = message.photo[-1]  # mayor resolución disponible

    await state.update_data(file_id=photo.file_id)
    await state.set_state(AnalysisFlow.waiting_site_name)

    await message.reply(
        "📸 Fotografía recibida.\n\n"
        "¿Cuál es el nombre del sitio rupestre? \n"
        "_(Ej: Villa de Leyva - Sector Norte)_",
        parse_mode="Markdown",
    )
    logger.info(f"Foto recibida de usuario {message.from_user.id}")


@router.message(AnalysisFlow.waiting_site_name)
async def handle_site_name(message: Message, state: FSMContext):
    """Usuario envía el nombre del sitio → pedir coordenadas."""
    await state.update_data(site_name=message.text)
    await state.set_state(AnalysisFlow.waiting_coordinates)

    await message.reply(
        f"✅ Sitio: *{message.text}*\n\n"
        "Ahora envía las coordenadas GPS en formato:\n"
        "`latitud, longitud`\n"
        "_(Ej: 5.634, -73.525)_",
        parse_mode="Markdown",
    )


@router.message(AnalysisFlow.waiting_coordinates)
async def handle_coordinates(message: Message, state: FSMContext):
    """Usuario envía coordenadas → disparar pipeline de análisis."""
    try:
        lat, lon = [float(x.strip()) for x in message.text.split(",")]
    except ValueError:
        await message.reply(
            "⚠️ Formato inválido. Envía: `latitud, longitud`", parse_mode="Markdown"
        )
        return

    data = await state.get_data()
    await state.set_state(AnalysisFlow.processing)

    await message.reply(
        "⚙️ *Procesando análisis...*\n"
        "El sistema está analizando el sitio. Esto puede tardar algunos minutos. "
        "Te notificaré cuando la ficha ICANH esté lista.",
        parse_mode="Markdown",
    )

    # TODO: llamar a la API y encolar la tarea
    logger.info(f"Análisis iniciado: {data.get('site_name')} ({lat}, {lon})")
