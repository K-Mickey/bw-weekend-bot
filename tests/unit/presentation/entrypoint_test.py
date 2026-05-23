from unittest.mock import ANY, AsyncMock, Mock, patch

import pytest

from src.config import settings
from src.presentation.entrypoint import connect_telegram_webhook, connect_vk_webhook, on_startup_telegram, start_webhook

PREFIX = "src.presentation.entrypoint"


@pytest.fixture
def telegram_bot():
    bot = Mock()
    bot.set_my_commands = AsyncMock()
    bot.set_webhook = AsyncMock()
    return bot


def test_start_webhook():
    with (
        patch(f"{PREFIX}.web.run_app") as mock_run_app,
        patch(f"{PREFIX}.connect_telegram_webhook") as mock_connect_telegram_webhook,
        patch(f"{PREFIX}.connect_vk_webhook") as mock_connect_vk_webhook,
    ):
        start_webhook()

        mock_connect_telegram_webhook.assert_called_once_with(ANY)
        mock_connect_vk_webhook.assert_called_once_with(ANY)
        mock_run_app.assert_called_once_with(
            ANY,
            host=settings.web_server_host,
            port=settings.web_server_port,
        )


def test_connect_telegram_webhook():
    with (
        patch(f"{PREFIX}.get_telegram_bot"),
        patch(f"{PREFIX}.get_telegram_dp") as mock_get_telegram_dp,
        patch(f"{PREFIX}.SimpleRequestHandler") as MockHandler,
    ):
        mock_app = Mock()
        connect_telegram_webhook(mock_app)

        mock_telegram_dp = mock_get_telegram_dp.return_value
        mock_telegram_dp.startup.register.assert_called_once()
        handler_instance = MockHandler.return_value
        handler_instance.register.assert_called_once_with(ANY, path=settings.telegram.webhook_path)


@pytest.mark.asyncio
async def test_on_startup_telegram(telegram_bot):
    with patch(f"{PREFIX}.get_telegram_commands", return_value=[]):
        await on_startup_telegram(telegram_bot)
        telegram_bot.set_my_commands.assert_called_once_with(commands=[])
        telegram_bot.set_webhook.assert_called_once_with(
            url=settings.telegram.webhook_url,
            secret_token=settings.telegram.webhook_secret,
        )


def test_connect_vk_webhook():
    with patch(f"{PREFIX}.get_vk_bot") as mock_get_vk_bot:
        mock_app = Mock()
        connect_vk_webhook(mock_app)

        mock_get_vk_bot.assert_called_once()
        mock_app.router.add_post.assert_called_once_with(settings.vk.webhook_path, ANY)
        mock_app.on_startup.append.assert_called_once_with(ANY)
