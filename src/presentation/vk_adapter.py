from vkbottle import Keyboard, Text
from vkbottle.bot import BotLabeler, Message

from src.application.usecases.navigate import navigate
from src.application.usecases.start_conversation import start_conversation
from src.domain.aggregates import Content
from src.domain.aggregates.menu_node import MenuNode
from src.domain.entities.media.photo_node import PhotoNode
from src.domain.entities.media.text_node import TextNode
from src.domain.entities.media.video_node import VideoNode
from src.domain.value_objects.network import Network

labeler = BotLabeler()


@labeler.message(text="/start")
async def start_handler(message: Message) -> None:
    user_id = message.from_id
    content = start_conversation(Network.VK, user_id)
    await _send_content(message, content)


@labeler.message(text="/help")
async def help_handler(message: Message) -> None:
    await message.answer(
        "Пишите нам, если что-то не работает или нужна помощь:\n\n"
        "- Автор бота Михаил: @k_mickey \n"
        "- Наше главенство Мария: +79101463516"
    )


@labeler.message()
async def text_handler(message: Message) -> None:
    text = message.text
    if not text:
        return
    try:
        user_id = message.from_id
        content = navigate(Network.VK, user_id, text)
        await _send_content(message, content)
    except ValueError as e:
        await message.answer(f"Error: {e}")


async def _send_content(message: Message, content: Content) -> None:
    keyboard = None
    if isinstance(content, MenuNode):
        keyboard = _create_keyboard(content)

    posts = content.content if isinstance(content, MenuNode) else [content]

    for post in posts:
        for media in post.media:
            if isinstance(media, TextNode):
                await message.answer(media.text, keyboard=keyboard)
            elif isinstance(media, PhotoNode):
                # photo uploader?
                await message.answer(
                    attachment=media.url,
                    message=media.description or "",
                    keyboard=keyboard,
                )
            elif isinstance(media, VideoNode):
                # video uploader??
                await message.answer(
                    attachment=media.url,
                    message=media.description or "",
                    keyboard=keyboard,
                )
            else:
                # unsupported media type – silently ignore
                pass


def _create_keyboard(content: MenuNode) -> Keyboard:
    keyboard = Keyboard(inline=False)
    for row in content.keyboard:
        for button in row:
            keyboard.add(Text(button.text))
        keyboard.row()
    return keyboard
