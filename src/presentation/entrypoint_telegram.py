import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

from src.application.services import NavigationService, TelegramMessageSender
from src.config import settings
from src.infrastructure.content_repository import LocalContentRepository
from src.infrastructure.file_cache import SQLiteMediaCache
from src.infrastructure.state_store import SQLiteStateStore
from src.presentation.telegram_router import router

logger = logging.getLogger(__name__)


async def start_polling() -> None:
    async with get_telegram_bot() as bot:
        dp = await get_telegram_dp()
        dp.startup.register(set_commands)
        logger.info("Starting Telegram bot in polling mode...")
        await dp.start_polling(bot)


def get_telegram_bot() -> Bot:
    return Bot(token=settings.telegram.bot_token, default=DefaultBotProperties(parse_mode="HTML"))


async def get_telegram_dp() -> Dispatcher:
    cache = await SQLiteMediaCache.get_instance()
    state_store = await SQLiteStateStore.get_instance()
    content_repository = LocalContentRepository()

    dp = Dispatcher(
        message_sender=TelegramMessageSender(
            cache=cache,
            content_repository=content_repository,
        ),
        navigation_service=NavigationService(
            state_store=state_store,
            content_repository=content_repository,
        ),
    )
    dp.include_router(router)
    return dp


async def set_commands(bot: Bot) -> None:
    await bot.set_my_commands(commands=get_telegram_commands())


def get_telegram_commands() -> list[BotCommand]:
    return [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/help", description="Помощь"),
    ]


if __name__ == "__main__":
    logging.basicConfig(level=settings.log_level)
    asyncio.run(start_polling())
