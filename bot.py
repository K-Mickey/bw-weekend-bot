import logging
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from handlers import router
from settings import settings

logger = logging.getLogger(__name__)


async def start_polling() -> None:
    async with Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    ).context() as bot:
        await bot.set_my_commands(commands=_get_commands())
        dp = Dispatcher(storage=_get_storage(settings.db_path))
        dp.include_router(router)

        logger.info("Bot started")
        await dp.start_polling(bot)


def start_webhook() -> None:
    dp = Dispatcher(srorage=_get_storage(settings.db_path))
    dp.include_router(router)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp.startup.register(_on_startup)

    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.webhook_secret,
    )
    webhook_requests_handler.register(app, path=settings.webhook_path)
    setup_application(app, dp, bot=bot)

    logger.info("Bot started with webhook")
    web.run_app(
        app=app,
        host=settings.web_server_host,
        port=settings.web_server_port,
    )


async def _on_startup(bot: Bot):
    await bot.set_my_commands(commands=_get_commands())
    await bot.set_webhook(
        url=settings.webhook_url,
        secret_token=settings.webhook_secret,
    )
    logger.info("Webhook set successfully")


def _get_storage(db_path: Path) -> BaseStorage:
    logger.debug("Creating memory storage")
    return MemoryStorage()


def _get_commands() -> list[BotCommand]:
    return [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/help", description="Помощь"),
    ]
