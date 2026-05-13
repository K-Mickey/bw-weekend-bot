import copy
import logging
from abc import ABC, abstractmethod

from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile

from settings import settings

logger = logging.getLogger(__name__)


class Button:
    def __init__(self, text: str, source: str):
        self.text = text
        self.source = source


class Event:
    def __init__(self, *messages):
        self.messages: list[MessageContent] = list(messages)

    def get_button(self, name: str) -> Button | None:
        for message in self.messages:
            if button := message.get_button(name):
                return button
        return None

    def copy_and_set_kb(self, number_message: int, keyboard: list[list[Button]]):
        new_event = copy.deepcopy(self)
        new_event.messages[number_message].keyboard = keyboard
        return new_event


class ButtonMixin:
    keyboard: list[list[Button]] = []

    def get_button(self, name: str) -> Button | None:
        for row in self.keyboard:
            for button in row:
                if button.text == name:
                    return button
        return None

    def create_kb(self) -> ReplyKeyboardMarkup | None:
        if not self.keyboard:
            return None

        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=text.text) for text in row]
                for row in self.keyboard
            ],
            resize_keyboard=True,
        )


class MessageContent(ABC, ButtonMixin):
    @abstractmethod
    async def answer(self, message: Message): ...


class Text(MessageContent):
    def __init__(self, text: str, keyboard: list[list[Button]] = None):
        self.text = text
        self.keyboard = keyboard or []

    async def answer(self, message: Message):
        kb = self.create_kb()
        await message.answer(self.text, reply_markup=kb)


class Image(MessageContent):
    file_id = None

    def __init__(
        self, path: str, caption: str = "", keyboard: list[list[Button]] = None
    ):
        self.path = path
        self.caption = caption
        self.keyboard = keyboard or []

    async def answer(self, message: Message):
        kb = self.create_kb()
        caption = self.caption if self.caption else None

        try:
            await message.answer_photo(
                photo=self.file_id, caption=caption, reply_markup=kb
            )
            logger.debug(f"Image sent with id {self.file_id}")
        except Exception:
            img = FSInputFile(settings.img_path / self.path)
            image_message = await message.answer_photo(
                photo=img, caption=caption, reply_markup=kb
            )
            self.file_id = image_message.photo[-1].file_id
            logger.info(f"Image saved with id {self.file_id}")


class Video(MessageContent):
    file_id = None

    def __init__(
        self, path: str, caption: str = "", keyboard: list[list[Button]] = None
    ):
        self.path = path
        self.caption = caption
        self.keyboard = keyboard or []

    async def answer(self, message: Message):
        kb = self.create_kb()
        caption = self.caption if self.caption else None

        try:
            await message.answer_video(
                video=self.file_id, caption=caption, reply_markup=kb
            )
            logger.debug(f"Video sent with id {self.file_id}")
        except Exception:
            video = FSInputFile(settings.video_path / self.path)
            video_message = await message.answer_video(
                video=video, caption=caption, reply_markup=kb
            )
            self.file_id = video_message.video.file_id
            logger.info(f"Video saved with id {self.file_id}")
