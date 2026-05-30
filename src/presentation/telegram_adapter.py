import logging
from typing import Iterable

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    ErrorEvent,
    FSInputFile,
    InputMediaPhoto,
    InputMediaVideo,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from src.application.usecases.get_content import get_content_by_id
from src.application.usecases.navigate import navigate
from src.application.usecases.start_conversation import start_conversation
from src.domain.aggregates import Content, PostNode
from src.domain.aggregates.menu_node import MenuNode
from src.domain.entities.media.photo_node import PhotoNode
from src.domain.entities.media.text_node import TextNode
from src.domain.entities.media.video_node import VideoNode
from src.domain.value_objects.network import Network
from src.domain.value_objects.nodes import NodeName
from src.infrastructure.content_repository import ContentNotFoundException
from src.infrastructure.file_cache import get_cache
from src.infrastructure.file_cache.exceptions import MediaCacheError
from src.infrastructure.file_cache.value_objects.cache_key import CacheKey
from src.infrastructure.file_cache.value_objects.cache_record import CacheRecord
from src.infrastructure.file_provider import get_file_path

router = Router()
logger = logging.getLogger(__name__)


@router.errors()
async def handle_errors(event: ErrorEvent) -> None:
    logger.error(f"Error: {event.exception}")
    message = None
    update = event.update

    if update.message:
        message = update.message
    elif update.callback_query:
        message = update.callback_query.message
    else:
        logger.error(f"Unknown update type: {update}")

    if isinstance(event.exception, TelegramForbiddenError):
        logging.warning("User blocked the bot.")
        return

    if message:
        chat_id = message.chat.id
        try:
            content = get_content_by_id(NodeName.ERROR)
            await _send_content(message, content)
        except ContentNotFoundException:
            logger.error("Create error node")
            return
        except Exception as e:
            logging.error(f"Error: {e}")
            logging.exception(f"Error while sending error message to user {chat_id}")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    logger.debug("Start handler is called")
    user_id = message.from_user.id

    try:
        content = start_conversation(Network.TELEGRAM, user_id)
    except ContentNotFoundException:
        logger.error("Create start node")
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

    await _send_content(message, content)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    logger.debug("Help handler is called")

    try:
        content = get_content_by_id(NodeName.HELP)
    except ContentNotFoundException:
        logger.error("Create help node")
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

    await _send_content(message, content)


@router.message(F.text)
async def handle_text_message(message: Message) -> None:
    logger.debug("Text handler is called")
    user_id = message.from_user.id
    text = message.text
    if not text:
        return

    content = navigate(Network.TELEGRAM, user_id, text)
    logger.debug(f"Navigated to {content.id}")
    await _send_content(message, content)


async def _send_content(message: Message, content: Content) -> None:
    logger.debug("Send content is called")

    posts = content.content if isinstance(content, MenuNode) else [content]
    for post in posts:
        if len(post.media) == 0:
            logger.warning("Post has no media")
        elif len(post.media) == 1:
            [media] = post.media
            keyboard = _create_keyboard(post)
            logger.debug(f"Created keyboard: {keyboard}")
            match media:
                case TextNode():
                    await message.answer(media.text, reply_markup=keyboard)
                case PhotoNode():
                    await _send_photo_with_cache(message, media, keyboard)
                case VideoNode():
                    await _send_video_with_cache(message, media, keyboard)
                case _:
                    raise ValueError(f"Unsupported media type: {media}")
        else:
            await _send_group_media_with_cache(message, post.media)


def _create_keyboard(content: PostNode) -> ReplyKeyboardMarkup:
    rows = []
    for row in content.keyboard:
        buttons = [KeyboardButton(text=btn.text) for btn in row]
        rows.append(buttons)
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


async def _send_photo_with_cache(
    message: Message,
    photo: PhotoNode,
    keyboard: ReplyKeyboardMarkup | None = None,
):
    cache = await get_cache()

    cache_key = CacheKey.create(photo, Network.TELEGRAM)

    try:
        cache_record = await cache.get(cache_key)
        await message.answer_photo(
            photo=cache_record.file_id,
            caption=photo.description,
            reply_markup=keyboard,
        )
    except (TelegramBadRequest, MediaCacheError):
        file_path = get_file_path(photo)
        file = FSInputFile(file_path)
        photo_message = await message.answer_photo(
            photo=file,
            caption=photo.description,
            reply_markup=keyboard,
        )

        await _update_cache_from_messages([photo], [photo_message])


async def _send_video_with_cache(
    message: Message,
    video: VideoNode,
    keyboard: ReplyKeyboardMarkup | None = None,
):
    cache = await get_cache()

    cache_key = CacheKey.create(video, Network.TELEGRAM)

    try:
        cache_record = await cache.get(cache_key)
        await message.answer_video(
            video=cache_record.file_id,
            caption=video.description,
            reply_markup=keyboard,
        )
    except (TelegramBadRequest, MediaCacheError):
        file_path = get_file_path(video)
        file = FSInputFile(file_path)
        video_message = await message.answer_video(
            video=file,
            caption=video.description,
            reply_markup=keyboard,
        )

        await _update_cache_from_messages([video], [video_message])


async def _send_group_media_with_cache(
    message: Message,
    media: list[PhotoNode | VideoNode],
):

    media_list, has_update_cache = await _build_media_list(media, from_cache=True)
    try:
        messages = await message.answer_media_group(media_list)
        if has_update_cache:
            await _update_cache_from_messages(media, messages)

    except TelegramBadRequest:
        media_list, _ = await _build_media_list(media, from_cache=False)
        messages = await message.answer_media_group(media_list)
        await _update_cache_from_messages(media, messages)


async def _build_media_list(
    media: list[PhotoNode | VideoNode],
    from_cache: bool = False,
) -> tuple[list[InputMediaPhoto | InputMediaVideo], bool]:

    cache = await get_cache()

    result = []
    has_update_cache = False
    for node in media:
        media_source = None

        if from_cache:
            try:
                cache_key = CacheKey.create(node, Network.TELEGRAM)
                cache_record = await cache.get(cache_key)
                media_source = cache_record.file_id

            except MediaCacheError as e:
                has_update_cache = True
                logger.debug(e)

        if not media_source:
            media_source = FSInputFile(get_file_path(node))

        match node:
            case PhotoNode():
                item = InputMediaPhoto(media=media_source, caption=node.description)
            case VideoNode():
                item = InputMediaVideo(media=media_source, caption=node.description)
            case _:
                raise ValueError(f"Unsupported media type: {node}")

        result.append(item)
    return result, has_update_cache


async def _update_cache_from_messages(
    media: Iterable[PhotoNode | VideoNode],
    messages: Iterable[Message],
) -> None:
    cache = await get_cache()

    for message, node in zip(messages, media):
        cache_key = CacheKey.create(node, Network.TELEGRAM)

        if message.photo:
            new_file_id = message.photo[-1].file_id
        elif message.video:
            new_file_id = message.video.file_id
        else:
            logger.warning(f"No media found in message: {message}")

        record = CacheRecord.from_file(file_id=new_file_id, file_path=get_file_path(node))
        await cache.add(cache_key, record)
