import logging

from vkbottle.bot import BotLabeler, Message
from vkbottle.dispatch.rules.base import CommandRule, TextRule

from src.application.services import MessageSender, NavigationService
from src.domain.value_objects.network import Network
from src.domain.value_objects.node import NodeName

labeler = BotLabeler()

logger = logging.getLogger(__name__)


@labeler.private_message(CommandRule("начать") | TextRule("начать", ignore_case=True))
async def cmd_start(message: Message, message_sender: MessageSender, navigation_service: NavigationService) -> None:
    logger.debug("Start handler is called")
    user_id = message.from_id

    try:
        content = await navigation_service.start_conversation(Network.VK, user_id)
        await message_sender.send_content(message, content)

    except Exception:
        await message_sender.send_error_message(message)
        raise


@labeler.private_message(CommandRule("помощь"))
async def cmd_help(message: Message, message_sender: MessageSender, navigation_service: NavigationService) -> None:
    logger.debug("Help handler is called")
    try:
        content = navigation_service.get_content_by_id(NodeName.HELP)
        await message_sender.send_content(message, content)

    except Exception:
        await message_sender.send_error_message(message)
        raise


@labeler.private_message()
async def text_handler(message: Message, message_sender: MessageSender, navigation_service: NavigationService) -> None:
    logger.debug("Text handler is called")
    user_id = message.from_id
    text = message.text.strip()
    if not text:
        return

    try:
        content = await navigation_service.navigate(Network.VK, user_id, text)
        logger.debug(f"Navigated to {content.id}")
        await message_sender.send_content(message, content)

    except Exception:
        await message_sender.send_error_message(message)
        raise
