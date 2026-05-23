import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

from src.config import settings
from src.presentation.telegram_adapter import router

logger = logging.getLogger(__name__)


async def start_polling() -> None:
    async with get_telegram_bot() as bot:
        dp = get_telegram_dp()
        dp.startup.register(set_commands)
        logger.info("Starting Telegram bot in polling mode...")
        await dp.start_polling(bot)


def get_telegram_bot() -> Bot:
    return Bot(token=settings.telegram.bot_token, default=DefaultBotProperties(parse_mode="HTML"))


def get_telegram_dp() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(router)
    return dp


def set_commands(bot: Bot) -> None:
    bot.set_my_commands(commands=get_telegram_commands())


def get_telegram_commands() -> list[BotCommand]:
    return [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/help", description="Помощь"),
    ]
