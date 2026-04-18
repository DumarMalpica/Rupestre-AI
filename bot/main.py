"""Entry point del bot de Telegram."""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.handlers import photo_handler
from core.config import settings
from core.logger import get_logger

logger = get_logger("bot.main")


async def main():
    if not settings.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN no configurado en .env")
        return

    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()

    dp.include_router(photo_handler.router)

    logger.info("Bot iniciado — esperando mensajes...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
