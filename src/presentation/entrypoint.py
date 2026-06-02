import asyncio
import logging

from aiogram import Bot as TelegramBot
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from vkbottle.callback import BotCallback

from src.config import settings
from src.presentation.entrypoint_telegram import get_telegram_bot, get_telegram_commands, get_telegram_dp
from src.presentation.entrypoint_vk import get_vk_bot

logger = logging.getLogger(__name__)


def start_webhook() -> None:
    app = web.Application()

    connect_telegram_webhook(app)
    connect_vk_webhook(app)

    host = settings.web_server_host
    port = settings.web_server_port
    logger.info("Starting Telegram bot in webhook mode on %s:%s", host, port)
    web.run_app(app, host=host, port=port)


def connect_telegram_webhook(app: web.Application):
    telegram_bot = get_telegram_bot()

    telegram_dp = asyncio.run(get_telegram_dp(telegram_bot))
    telegram_dp.startup.register(on_startup_telegram)

    handler = SimpleRequestHandler(
        dispatcher=telegram_dp,
        bot=telegram_bot,
        secret_token=settings.telegram.webhook_secret,
    )
    handler.register(app, path=settings.telegram.webhook_path)
    setup_application(app, telegram_dp, bot=telegram_bot)


async def on_startup_telegram(bot: TelegramBot):
    await bot.set_my_commands(commands=get_telegram_commands())

    webhook_url = settings.telegram.webhook_url
    secret_token = settings.telegram.webhook_secret
    if webhook_url:
        await bot.set_webhook(url=webhook_url, secret_token=secret_token)
        logger.info("Webhook set to %s", webhook_url)


def connect_vk_webhook(app: web.Application):
    secret_key = ""
    confirmation_code = ""

    callback = BotCallback(
        url=settings.vk.webhook_url,
        title=settings.vk.webhook_title,
        secret_key=settings.vk.webhook_secret,
    )
    vk_bot = asyncio.run(get_vk_bot(callback))

    async def vk_webhook(request: web.Request):
        try:
            event = await request.json()
        except Exception:
            return web.Response(status=400, text="Invalid JSON")

        if event.get("type") == "confirmation":
            return web.Response(text=confirmation_code)

        if secret_key and event.get("secret") != secret_key:
            return web.Response(status=403, text="Forbidden")

        asyncio.create_task(safe_process_event(event))
        return web.Response(text="ok")

    async def on_startup_vk(app: web.Application):
        nonlocal confirmation_code, secret_key
        confirmation_code, secret_key = await vk_bot.setup_webhook()

    async def safe_process_event(event: dict):
        try:
            await vk_bot.process_event(event)
        except Exception as e:
            logger.error("Failed to process event: %s", e)

    app.router.add_post(settings.vk.webhook_path, vk_webhook)
    app.on_startup.append(on_startup_vk)
