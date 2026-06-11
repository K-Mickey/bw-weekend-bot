import logging

from vkbottle.bot import BotLabeler, Message
from vkbottle.dispatch.rules.base import CommandRule

from src.application.services import MessageSender
from src.application.usecases.get_content import get_content_by_id
from src.application.usecases.navigate import navigate
from src.application.usecases.start_conversation import start_conversation
from src.domain.value_objects.network import Network
from src.domain.value_objects.node import NodeName
from src.infrastructure.state_store import StateStore

labeler = BotLabeler()

logger = logging.getLogger(__name__)


@labeler.private_message(CommandRule("начать"))
async def cmd_start(message: Message, message_sender: MessageSender, state_store: StateStore) -> None:
    logger.debug("Start handler is called")
    user_id = message.from_id

    try:
        content = await start_conversation(state_store, Network.TELEGRAM, user_id)
        await message_sender.send_content(message, content)

    except Exception:
        await message_sender.send_error_message(message)
        raise


@labeler.private_message(CommandRule("помощь"))
async def cmd_help(message: Message, message_sender: MessageSender) -> None:
    logger.debug("Help handler is called")
    try:
        content = get_content_by_id(NodeName.HELP)
        await message_sender.send_content(message, content)

    except Exception:
        await message_sender.send_error_message(message)
        raise


@labeler.private_message()
async def text_handler(message: Message, message_sender: MessageSender, state_store: StateStore) -> None:
    logger.debug("Text handler is called")
    user_id = message.from_id
    text = message.text.strip()
    if not text:
        return

    try:
        content = await navigate(state_store, Network.TELEGRAM, user_id, text)
        logger.debug(f"Navigated to {content.id}")
        await message_sender.send_content(message, content)

    except Exception:
        await message_sender.send_error_message(message)
        raise
