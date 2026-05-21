import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from src.config import settings
from src.presentation.telegram_adapter import router

logger = logging.getLogger(__name__)


async def start_polling() -> None:
    bot_token = settings.BOT_TOKEN_TELEGRAM
    if not bot_token:
        logger.error("BOT_TOKEN_TELEGRAM not set in environment")
        return

    async with Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    ) as bot:
        await bot.set_my_commands(commands=_get_commands())
        dp = Dispatcher()
        dp.include_router(router)
        logger.info("Starting Telegram bot in polling mode...")
        await dp.start_polling(bot)


def start_webhook() -> None:
    bot_token = settings.BOT_TOKEN_TELEGRAM
    if not bot_token:
        logger.error("BOT_TOKEN_TELEGRAM not set in environment")
        return
    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp.include_router(router)

    dp.startup.register(on_startup)

    app = web.Application()
    handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.WEBHOOK_SECRET,
    )
    handler.register(app, path=settings.WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    host = settings.WEB_SERVER_HOST
    port = settings.WEB_SERVER_PORT
    logger.info("Starting Telegram bot in webhook mode on %s:%s", host, port)
    web.run_app(app, host=host, port=port)


async def on_startup(bot: Bot):
    await bot.set_my_commands(commands=_get_commands())
    webhook_url = settings.WEBHOOK_URL
    secret_token = settings.WEBHOOK_SECRET
    if webhook_url:
        await bot.set_webhook(url=webhook_url, secret_token=secret_token)
        logger.info("Webhook set to %s", webhook_url)


def _get_commands() -> list[BotCommand]:
    return [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/help", description="Помощь"),
    ]
