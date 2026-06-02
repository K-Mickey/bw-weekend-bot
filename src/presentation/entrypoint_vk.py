import asyncio
import logging

from vkbottle import BaseMiddleware, ErrorHandler
from vkbottle.bot import Bot, Message
from vkbottle.callback import BotCallback

from src.application.services import MessageSender
from src.application.services.vk_message_sender import VKMessageSender
from src.config import settings
from src.infrastructure.file_cache import get_cache
from src.presentation.vk_labeler import labeler

logger = logging.getLogger(__name__)
error_handler = ErrorHandler()


class InjectionMiddleware(BaseMiddleware[Message]):
    _message_sender: MessageSender | None = None

    async def pre(self) -> None:
        self.send({"message_sender": self._message_sender})

    @classmethod
    def set_sender(cls, message_sender: MessageSender):
        cls._message_sender = message_sender


@error_handler.register_error_handler(Exception)
async def handle_errors(e: Exception) -> None:
    logger.error(f"Error: {e}")


async def start_polling() -> None:
    if not settings.bot_token_vk:
        logger.error("VK_TOKEN not set in environment")
        return

    bot = await get_vk_bot()
    logger.info("Starting VK bot in polling mode...")

    await bot.run_polling()


async def get_vk_bot(callback: BotCallback | None = None) -> Bot:
    bot = Bot(token=settings.vk.bot_token, labeler=labeler, callback=callback, error_handler=error_handler)

    cache = await get_cache()
    message_sender = VKMessageSender(bot, cache)

    middleware = InjectionMiddleware
    middleware.set_sender(message_sender)
    bot.labeler.message_view.register_middleware(middleware)

    return bot


if __name__ == "__main__":
    logging.basicConfig(level=settings.log_level)
    asyncio.run(start_polling())
