from unittest.mock import ANY, AsyncMock, patch

import pytest
from aiogram.types import BotCommand

from src.config import settings
from src.presentation.entrypoint_telegram import get_commands, start_polling


@pytest.mark.asyncio
async def test_start_polling_with_token():
    mock_bot = AsyncMock()
    mock_bot.__aenter__ = AsyncMock(return_value=mock_bot)
    mock_bot.__aexit__ = AsyncMock()

    with (
        patch("src.presentation.entrypoint_telegram.Bot", return_value=mock_bot) as MockBot,
        patch("src.presentation.entrypoint_telegram.Dispatcher") as MockDispatcher,
        patch("src.presentation.entrypoint_telegram.router") as mock_router,
        patch("src.presentation.entrypoint_telegram.get_commands", return_value=[]) as mock_get_commands,
    ):
        mock_dp = MockDispatcher.return_value
        mock_dp.start_polling = AsyncMock()

        await start_polling()

        MockBot.assert_called_once_with(
            token=settings.telegram.bot_token,
            default=ANY,
        )
        mock_bot.set_my_commands.assert_awaited_once_with(commands=mock_get_commands.return_value)
        MockDispatcher.assert_called_once()
        mock_dp.include_router.assert_called_once_with(mock_router)
        mock_dp.start_polling.assert_awaited_once_with(mock_bot)


def test_get_commands():
    commands = get_commands()
    assert all(isinstance(command, BotCommand) for command in commands)
