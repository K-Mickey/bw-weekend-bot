from unittest.mock import ANY, AsyncMock, Mock, patch

import pytest

from src.config import settings
from src.presentation.entrypoint import on_startup, start_webhook


@pytest.fixture
def telegram_bot():
    bot = Mock()
    bot.set_my_commands = AsyncMock()
    bot.set_webhook = AsyncMock()
    return bot


def test_start_webhook():
    with (
        patch("src.presentation.entrypoint.web.run_app") as mock_run_app,
        patch("src.presentation.entrypoint.Bot") as MockBot,
        patch("src.presentation.entrypoint.SimpleRequestHandler") as MockHandler,
    ):
        start_webhook()

        MockBot.assert_called_once_with(token=settings.telegram.bot_token, default=ANY)

        handler_instance = MockHandler.return_value
        handler_instance.register.assert_called_once_with(ANY, path=settings.telegram.webhook_path)

        mock_run_app.assert_called_once_with(
            ANY,
            host=settings.web_server_host,
            port=settings.web_server_port,
        )


@pytest.mark.asyncio
async def test_on_startup(telegram_bot):
    with patch("src.presentation.entrypoint.get_commands", return_value=[]):
        await on_startup(telegram_bot)
        telegram_bot.set_my_commands.assert_called_once_with(commands=[])
        telegram_bot.set_webhook.assert_called_once_with(
            url=settings.telegram.webhook_url,
            secret_token=settings.telegram.webhook_secret,
        )
