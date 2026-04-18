"""Estados de la conversación del bot con el arqueólogo."""

from aiogram.fsm.state import State, StatesGroup


class AnalysisFlow(StatesGroup):
    """Flujo completo de análisis de un sitio rupestre."""

    waiting_photo = State()  # Esperando fotografía del sitio
    waiting_site_name = State()  # Esperando nombre del sitio
    waiting_coordinates = State()  # Esperando coordenadas GPS
    processing = State()  # Pipeline corriendo (no acepta input)
    done = State()  # Ficha entregada
