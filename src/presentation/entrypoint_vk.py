import asyncio
import logging

from content_repository import LocalContentRepository
from vkbottle import BaseMiddleware, ErrorHandler
from vkbottle.bot import Bot, Message
from vkbottle.callback import BotCallback

from src.application.services import MessageSender, NavigationService
from src.application.services.vk_message_sender import VKMessageSender
from src.config import settings
from src.infrastructure.file_cache import SQLiteMediaCache
from src.infrastructure.state_store import MemoryStateStore
from src.presentation.vk_labeler import labeler

logger = logging.getLogger(__name__)
error_handler = ErrorHandler()


class InjectionMiddleware(BaseMiddleware[Message]):
    _message_sender: MessageSender | None = None
    _navigation_service: NavigationService | None = None

    async def pre(self) -> None:
        self.send(
            {
                "message_sender": self._message_sender,
                "navigation_service": self._navigation_service,
            }
        )

    @classmethod
    def set_sender(cls, message_sender: MessageSender):
        cls._message_sender = message_sender

    @classmethod
    def set_navigation_service(cls, navigation_service: NavigationService):
        cls._navigation_service = navigation_service


@error_handler.register_error_handler(Exception)
async def handle_errors(e: Exception) -> None:
    logger.error(f"Error: {e}")


def start_polling() -> None:
    if not settings.vk.bot_token:
        logger.error("VK_TOKEN not set in environment")
        return

    bot = get_vk_bot()
    logger.info("Starting VK bot in polling mode...")

    bot.run_forever()


def get_vk_bot(callback: BotCallback | None = None) -> Bot:
    bot = Bot(
        token=settings.vk.bot_token,
        labeler=labeler,
        callback=callback,
        error_handler=error_handler,
    )

    cache, state_store = asyncio.gather(SQLiteMediaCache.get_instance(), MemoryStateStore.get_instance())
    message_sender = VKMessageSender(
        bot=bot,
        cache=cache,
        content_repository=LocalContentRepository(),
    )
    navigation_service = NavigationService(
        state_store=state_store,
        content_repository=LocalContentRepository(),
    )

    middleware = InjectionMiddleware
    middleware.set_sender(message_sender)
    middleware.set_navigation_service(navigation_service)
    bot.labeler.message_view.register_middleware(middleware)

    return bot


if __name__ == "__main__":
    logging.basicConfig(level=settings.log_level)
    start_polling()
