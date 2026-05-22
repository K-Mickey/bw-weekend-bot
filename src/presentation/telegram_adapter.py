from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from src.application.usecases.navigate import navigate
from src.application.usecases.start_conversation import start_conversation
from src.domain.aggregates import Content
from src.domain.aggregates.menu_node import MenuNode
from src.domain.entities.media.photo_node import PhotoNode
from src.domain.entities.media.text_node import TextNode
from src.domain.entities.media.video_node import VideoNode
from src.domain.value_objects.network import Network

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_id = message.from_user.id
    content = start_conversation(Network.TELEGRAM, user_id)
    await _send_content(message, content)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        text="Пишите нам, если что-то не работает или нужна помощь:\n\n"
        "- Автор бота Михаил: @k_mickey \n"
        "- Наше главенство Мария: +79101463516"
    )


@router.message(F.text)
async def handle_text_message(message: Message) -> None:
    user_id = message.from_user.id
    text = message.text
    if not text:
        return
    try:
        content = navigate(Network.TELEGRAM, user_id, text)
        await _send_content(message, content)
    except ValueError as e:
        await message.answer(f"Error: {e}")


async def _send_content(message: Message, content: Content) -> None:
    keyboard: ReplyKeyboardMarkup | None = None
    if isinstance(content, MenuNode):
        keyboard = _create_keyboard(content)

    posts = content.content if isinstance(content, MenuNode) else [content]

    for post in posts:
        for media in post.media:
            if isinstance(media, TextNode):
                await message.answer(media.text, reply_markup=keyboard)
            elif isinstance(media, PhotoNode):
                await message.answer_photo(
                    photo=media.url,
                    caption=media.description or "",
                    reply_markup=keyboard,
                )
            elif isinstance(media, VideoNode):
                await message.answer_video(
                    video=media.url,
                    caption=media.description or "",
                    reply_markup=keyboard,
                )
            else:
                # TODO: add error log
                pass


def _create_keyboard(content: MenuNode) -> ReplyKeyboardMarkup:
    rows = []
    for row in content.keyboard:
        buttons = [KeyboardButton(text=btn.text) for btn in row]
        rows.append(buttons)
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
