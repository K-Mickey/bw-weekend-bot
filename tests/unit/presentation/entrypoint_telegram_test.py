from unittest.mock import ANY, AsyncMock, Mock, patch

import pytest
from aiogram.types import BotCommand

from src.config import settings
from src.presentation.entrypoint_telegram import _get_commands, on_startup, start_polling, start_webhook


@pytest.fixture
def bot():
    bot = Mock()
    bot.set_my_commands = AsyncMock()
    bot.set_webhook = AsyncMock()
    return bot


@pytest.fixture
def mock_get_commands():
    with patch("src.presentation.entrypoint_telegram._get_commands", return_value=[]):
        yield


@pytest.mark.asyncio
async def test_start_polling_with_token():
    mock_bot = AsyncMock()
    mock_bot.__aenter__ = AsyncMock(return_value=mock_bot)
    mock_bot.__aexit__ = AsyncMock()

    with (
        patch("src.presentation.entrypoint_telegram.Bot", return_value=mock_bot) as MockBot,
        patch("src.presentation.entrypoint_telegram._get_commands", return_value=[]) as mock_get_commands,
        patch("src.presentation.entrypoint_telegram.Dispatcher") as MockDispatcher,
        patch("src.presentation.entrypoint_telegram.router") as mock_router,
    ):
        mock_dp = MockDispatcher.return_value
        mock_dp.start_polling = AsyncMock()

        await start_polling()

        MockBot.assert_called_once_with(
            token=settings.bot_token_telegram,
            default=ANY,
        )
        mock_bot.set_my_commands.assert_awaited_once_with(commands=mock_get_commands.return_value)
        MockDispatcher.assert_called_once()
        mock_dp.include_router.assert_called_once_with(mock_router)
        mock_dp.start_polling.assert_awaited_once_with(mock_bot)


def test_start_webhook():
    with (
        patch("src.presentation.entrypoint_telegram.web.run_app") as mock_run_app,
        patch("src.presentation.entrypoint_telegram.Bot") as MockBot,
        patch("src.presentation.entrypoint_telegram.SimpleRequestHandler") as MockHandler,
    ):
        start_webhook()

        MockBot.assert_called_once_with(token=settings.bot_token_telegram, default=ANY)

        handler_instance = MockHandler.return_value
        handler_instance.register.assert_called_once_with(ANY, path=settings.webhook_path)

        mock_run_app.assert_called_once_with(
            ANY,
            host=settings.web_server_host,
            port=settings.web_server_port,
        )


@pytest.mark.asyncio
async def test_on_startup(bot, mock_get_commands):
    await on_startup(bot)
    bot.set_my_commands.assert_called_once_with(commands=[])
    bot.set_webhook.assert_called_once_with(
        url=settings.webhook_url,
        secret_token=settings.webhook_secret,
    )


def test_get_commands():
    commands = _get_commands()
    assert all(isinstance(command, BotCommand) for command in commands)
