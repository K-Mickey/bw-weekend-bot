import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    ErrorEvent,
    Message,
)

from src.application.services import MessageSender, NavigationService
from src.domain.value_objects.network import Network
from src.domain.value_objects.node import NodeName

router = Router()
logger = logging.getLogger(__name__)


@router.errors()
async def handle_errors(event: ErrorEvent) -> None:
    logger.error(f"Error: {event.exception}")


@router.message(CommandStart())
async def cmd_start(message: Message, message_sender: MessageSender, navigation_service: NavigationService) -> None:
    logger.debug("Start handler is called")
    user_id = message.from_user.id

    try:
        content = await navigation_service.start_conversation(Network.TELEGRAM, user_id)
        await message_sender.send_content(message, content)

    except Exception:
        await message_sender.send_error_message(message)
        raise


@router.message(Command("help"))
async def cmd_help(message: Message, message_sender: MessageSender, navigation_service: NavigationService) -> None:
    logger.debug("Help handler is called")
    try:
        content = navigation_service.get_content_by_id(NodeName.HELP)
        await message_sender.send_content(message, content)

    except Exception:
        await message_sender.send_error_message(message)
        raise


@router.message(F.text)
async def handle_text_message(
    message: Message, message_sender: MessageSender, navigation_service: NavigationService
) -> None:
    logger.debug("Text handler is called")
    user_id = message.from_user.id
    text = message.text.strip()
    if not text:
        return

    try:
        content = await navigation_service.navigate(Network.TELEGRAM, user_id, text)
        logger.debug(f"Navigated to {content.id}")
        await message_sender.send_content(message, content)

    except Exception:
        await message_sender.send_error_message(message)
        raise
