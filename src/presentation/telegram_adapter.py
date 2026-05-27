import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import FSInputFile, KeyboardButton, Message, ReplyKeyboardMarkup

from src.application.usecases.navigate import navigate
from src.application.usecases.start_conversation import start_conversation
from src.domain.aggregates import Content
from src.domain.aggregates.menu_node import MenuNode
from src.domain.entities.media.photo_node import PhotoNode
from src.domain.entities.media.text_node import TextNode
from src.domain.entities.media.video_node import VideoNode
from src.domain.value_objects.network import Network
from src.infrastructure.file_cache import get_cache
from src.infrastructure.file_cache.value_objects.cache_key import CacheKey
from src.infrastructure.file_cache.value_objects.cache_media_type import CacheMediaType
from src.infrastructure.file_cache.value_objects.cache_record import CacheRecord
from src.infrastructure.file_provider import get_file_path

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    logger.debug("Start handler is called")
    user_id = message.from_user.id
    content = start_conversation(Network.TELEGRAM, user_id)
    await _send_content(message, content)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    logger.debug("Help handler is called")
    await message.answer(
        text="Пишите нам, если что-то не работает или нужна помощь:\n\n"
        "- Автор бота Михаил: @k_mickey \n"
        "- Наше главенство Мария: +79101463516"
    )


@router.message(F.text)
async def handle_text_message(message: Message) -> None:
    logger.debug("Text handler is called")
    user_id = message.from_user.id
    text = message.text
    if not text:
        return
    try:
        content = navigate(Network.TELEGRAM, user_id, text)
        logger.debug(f"Navigated to {content.id}")
        await _send_content(message, content)
    except ValueError as e:
        logger.error(f"Error: {e}")
        await message.answer("Извините, что-то пошло не так")
        await cmd_start(message)


async def _send_content(message: Message, content: Content) -> None:
    logger.debug("Send content is called")
    keyboard: ReplyKeyboardMarkup | None = None
    if isinstance(content, MenuNode):
        keyboard = _create_keyboard(content)
        logger.debug(f"Created keyboard: {keyboard}")

    posts = content.content if isinstance(content, MenuNode) else [content]
    for post in posts:
        for media in post.media:
            match media:
                case TextNode():
                    await message.answer(media.text, reply_markup=keyboard)
                case PhotoNode():
                    await _send_photo_with_cache(message, media, keyboard)
                case VideoNode():
                    await _send_video_with_cache(message, media, keyboard)
                case _:
                    raise ValueError(f"Unsupported media type: {media}")


def _create_keyboard(content: MenuNode) -> ReplyKeyboardMarkup:
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

    cache_key = CacheKey(
        media_type=CacheMediaType.PHOTO,
        network=Network.TELEGRAM,
        key=photo.url,
    )

    try:
        cache_record = await cache.get(cache_key)
        await message.answer_photo(
            photo=cache_record.file_id,
            caption=photo.description,
            reply_markup=keyboard,
        )
    except Exception:
        file_path = get_file_path(photo)
        file = FSInputFile(file_path)
        photo_message = await message.answer_photo(
            photo=file,
            caption=photo.description,
            reply_markup=keyboard,
        )

        file_id = photo_message.photo[-1].file_id
        cache_record = CacheRecord.from_file(
            file_id=file_id,
            file_path=file_path,
        )

        await cache.add(cache_key, cache_record)


async def _send_video_with_cache(
    message: Message,
    video: VideoNode,
    keyboard: ReplyKeyboardMarkup | None = None,
):
    cache = await get_cache()

    cache_key = CacheKey(
        media_type=CacheMediaType.VIDEO,
        network=Network.TELEGRAM,
        key=video.url,
    )

    try:
        cache_record = await cache.get(cache_key)
        await message.answer_video(
            video=cache_record.file_id,
            caption=video.description,
            reply_markup=keyboard,
        )
    except Exception:
        file_path = get_file_path(video)
        file = FSInputFile(file_path)
        video_message = await message.answer_video(
            video=file,
            caption=video.description,
            reply_markup=keyboard,
        )

        file_id = video_message.video[-1].file_id
        cache_record = CacheRecord.from_file(
            file_id=file_id,
            file_path=file_path,
        )

        await cache.add(cache_key, cache_record)
