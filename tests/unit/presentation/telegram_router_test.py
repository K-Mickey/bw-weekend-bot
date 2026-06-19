from unittest.mock import ANY, Mock

import pytest

from src.application.services import MessageSender, NavigationService
from src.domain.value_objects.network import Network
from src.domain.value_objects.node import NodeName
from src.presentation.telegram_router import cmd_help, cmd_start, handle_text_message


@pytest.fixture
def message_sender():
    sender = Mock(spec=MessageSender)
    return sender


@pytest.fixture
def navigation_service():
    service = Mock(spec=NavigationService)
    return service


async def test_start(tg_message, message_sender, navigation_service):
    await cmd_start(tg_message, message_sender, navigation_service)
    navigation_service.start_conversation.assert_called_once_with(Network.TELEGRAM, tg_message.from_user.id)
    message_sender.send_content.assert_called_once_with(tg_message, navigation_service.start_conversation.return_value)


async def test_exception_start(tg_message, message_sender, navigation_service):
    navigation_service.start_conversation.side_effect = Exception
    with pytest.raises(Exception):
        await cmd_start(tg_message, message_sender, navigation_service)
    message_sender.send_error_message.assert_called_once_with(tg_message)


async def test_help(tg_message, message_sender, navigation_service):
    await cmd_help(tg_message, message_sender, navigation_service)
    navigation_service.get_content_by_id.assert_called_once_with(NodeName.HELP)
    message_sender.send_content.assert_called_once_with(tg_message, navigation_service.get_content_by_id.return_value)


async def test_exception_help(tg_message, message_sender, navigation_service):
    navigation_service.get_content_by_id.side_effect = Exception
    with pytest.raises(Exception):
        await cmd_help(tg_message, message_sender, navigation_service)
    message_sender.send_error_message.assert_called_once_with(tg_message)


async def test_text(tg_message, message_sender, navigation_service):
    await handle_text_message(tg_message, message_sender, navigation_service)
    navigation_service.navigate.assert_called_once_with(
        Network.TELEGRAM, tg_message.from_user.id, tg_message.text.strip()
    )
    message_sender.send_content.assert_called_once_with(tg_message, ANY)


async def test_exception_text(tg_message, message_sender, navigation_service):
    navigation_service.navigate.side_effect = Exception
    with pytest.raises(Exception):
        await handle_text_message(tg_message, message_sender, navigation_service)
    message_sender.send_error_message.assert_called_once_with(tg_message)
