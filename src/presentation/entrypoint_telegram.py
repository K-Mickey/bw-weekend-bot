import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

from src.config import settings
from src.presentation.telegram_adapter import router

logger = logging.getLogger(__name__)


async def start_polling() -> None:
    bot_token = settings.telegram.bot_token

    async with Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    ) as bot:
        await bot.set_my_commands(commands=get_commands())
        dp = Dispatcher()
        dp.include_router(router)
        logger.info("Starting Telegram bot in polling mode...")
        await dp.start_polling(bot)


def get_commands() -> list[BotCommand]:
    return [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/help", description="Помощь"),
    ]
