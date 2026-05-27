from unittest.mock import ANY, AsyncMock, patch

import pytest
from aiogram import Dispatcher, Router
from aiogram.types import BotCommand

from src.config import settings
from src.presentation.entrypoint_telegram import (
    get_telegram_bot,
    get_telegram_commands,
    get_telegram_dp,
    set_commands,
    start_polling,
)


@pytest.mark.asyncio
async def test_start_polling_with_token():
    mock_bot = AsyncMock()
    mock_bot.__aenter__ = AsyncMock(return_value=mock_bot)
    mock_bot.__aexit__ = AsyncMock()

    with (
        patch("src.presentation.entrypoint_telegram.get_telegram_bot", return_value=mock_bot),
        patch("src.presentation.entrypoint_telegram.get_telegram_dp") as MockDispatcher,
    ):
        mock_dp = MockDispatcher.return_value
        mock_dp.start_polling = AsyncMock()

        await start_polling()

        mock_dp.start_polling.assert_awaited_once_with(mock_bot)
        mock_dp.startup.register.assert_called_once_with(set_commands)


def test_get_commands():
    commands = get_telegram_commands()
    assert all(isinstance(command, BotCommand) for command in commands)


def test_bot():
    with patch("src.presentation.entrypoint_telegram.Bot") as mock_bot:
        get_telegram_bot()
        mock_bot.assert_called_once_with(
            token=settings.telegram.bot_token,
            default=ANY,
        )


def test_get_dp():
    with patch("src.presentation.entrypoint_telegram.router", new=Router()) as mock_router:
        dp = get_telegram_dp()
        assert isinstance(dp, Dispatcher)
        assert dp.sub_routers == [mock_router]


@pytest.mark.asyncio
async def test_set_commands():
    with patch("src.presentation.entrypoint_telegram.Bot") as mock_bot:
        mock_bot.set_my_commands = AsyncMock()
        await set_commands(mock_bot)
        mock_bot.set_my_commands.assert_called_once_with(commands=get_telegram_commands())
