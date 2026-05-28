import logging

from vkbottle import Keyboard, Text
from vkbottle.bot import BotLabeler, Message

from src.application.usecases.get_content import get_content_by_id
from src.application.usecases.navigate import navigate
from src.application.usecases.start_conversation import start_conversation
from src.domain.aggregates import Content
from src.domain.aggregates.menu_node import MenuNode
from src.domain.entities.media.photo_node import PhotoNode
from src.domain.entities.media.text_node import TextNode
from src.domain.entities.media.video_node import VideoNode
from src.domain.value_objects.network import Network
from src.domain.value_objects.nodes import NodeName

labeler = BotLabeler()
logger = logging.getLogger(__name__)


@labeler.message(text="/start")
async def start_handler(message: Message) -> None:
    logger.debug("Start handler is called")
    user_id = message.from_id
    content = start_conversation(Network.VK, user_id)
    await _send_content(message, content)


@labeler.message(text="/help")
async def help_handler(message: Message) -> None:
    logger.debug("Help handler is called")
    content = get_content_by_id(NodeName.HELP)
    if not content.media:
        logger.error("Create help node")
        return
    [post] = content.media
    await message.answer(post.text)


@labeler.message()
async def text_handler(message: Message) -> None:
    logger.debug("Text handler is called")
    text = message.text
    if not text:
        return
    try:
        user_id = message.from_id
        content = navigate(Network.VK, user_id, text)
        await _send_content(message, content)
    except ValueError as e:
        logger.error(f"Error: {e}")
        await message.answer("Извините, что-то пошло не так")
        await start_handler(message)


async def _send_content(message: Message, content: Content) -> None:
    logger.debug("Send content is called")
    keyboard = None
    if isinstance(content, MenuNode):
        keyboard = _create_keyboard(content)
        logger.debug(f"Created keyboard: {keyboard}")

    posts = content.content if isinstance(content, MenuNode) else [content]

    for post in posts:
        for media in post.media:
            if isinstance(media, TextNode):
                logger.debug(f"Sending text: {media.text}")
                await message.answer(media.text, keyboard=keyboard)
            elif isinstance(media, PhotoNode):
                logger.debug(f"Sending photo: {media.url}")
                # photo uploader?
                await message.answer(
                    attachment=media.url,
                    message=media.description or "",
                    keyboard=keyboard,
                )
            elif isinstance(media, VideoNode):
                logger.debug(f"Sending video: {media.url}")
                # video uploader??
                await message.answer(
                    attachment=media.url,
                    message=media.description or "",
                    keyboard=keyboard,
                )
            else:
                raise ValueError(f"Unsupported media type: {type(media)}")


def _create_keyboard(content: MenuNode) -> Keyboard:
    keyboard = Keyboard(inline=False)
    for row in content.keyboard:
        for button in row:
            keyboard.add(Text(button.text))
        keyboard.row()
    return keyboard
