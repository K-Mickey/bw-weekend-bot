import logging

from vkbottle.bot import Bot
from vkbottle.callback import BotCallback

from src.config import settings
from src.presentation.vk_adapter import labeler

logger = logging.getLogger(__name__)


async def start_polling() -> None:
    token = settings.bot_token_vk
    if not token:
        logger.error("VK_TOKEN not set in environment")
        return

    bot = get_vk_bot()
    logger.info("Starting VK bot in polling mode...")
    await bot.run_polling()


def get_vk_bot(callback: BotCallback | None = None) -> Bot:
    return Bot(
        token=settings.vk.bot_token,
        labeler=labeler,
        callback=callback,
    )
