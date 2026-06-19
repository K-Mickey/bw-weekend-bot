from unittest.mock import Mock

import pytest

from src.application.services import MessageSender, NavigationService
from src.domain.value_objects.network import Network
from src.domain.value_objects.node import NodeName
from src.presentation.vk_labeler import cmd_help, cmd_start, text_handler


@pytest.fixture
def message_sender():
    sender = Mock(spec=MessageSender)
    return sender


@pytest.fixture
def navigation_service():
    service = Mock(spec=NavigationService)
    return service


async def test_start(vk_message, message_sender, navigation_service):
    await cmd_start(vk_message, message_sender, navigation_service)
    navigation_service.start_conversation.assert_called_once_with(Network.VK, vk_message.from_id)
    message_sender.send_content.assert_called_once_with(vk_message, navigation_service.start_conversation.return_value)


async def test_exception_start(vk_message, message_sender, navigation_service):
    navigation_service.start_conversation.side_effect = Exception
    with pytest.raises(Exception):
        await cmd_start(vk_message, message_sender, navigation_service)
    message_sender.send_error_message.assert_called_once_with(vk_message)


async def test_help(vk_message, message_sender, navigation_service):
    await cmd_help(vk_message, message_sender, navigation_service)
    navigation_service.get_content_by_id.assert_called_once_with(NodeName.HELP)
    message_sender.send_content.assert_called_once_with(vk_message, navigation_service.get_content_by_id.return_value)


async def test_exception_help(vk_message, message_sender, navigation_service):
    navigation_service.get_content_by_id.side_effect = Exception
    with pytest.raises(Exception):
        await cmd_help(vk_message, message_sender, navigation_service)
    message_sender.send_error_message.assert_called_once_with(vk_message)


async def test_text_handler(vk_message, message_sender, navigation_service):
    await text_handler(vk_message, message_sender, navigation_service)
    navigation_service.navigate.assert_called_once_with(Network.TELEGRAM, vk_message.from_id, vk_message.text.strip())
    message_sender.send_content.assert_called_once_with(vk_message, navigation_service.navigate.return_value)


async def test_exception_text_handler(vk_message, message_sender, navigation_service):
    navigation_service.navigate.side_effect = Exception
    with pytest.raises(Exception):
        await text_handler(vk_message, message_sender, navigation_service)
    message_sender.send_error_message.assert_called_once_with(vk_message)
