import logging
from pathlib import Path

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from handlers import router as main_router

logger = logging.getLogger(__name__)


class BuBot:
    __slots__ = ("token", "db_path")

    def __init__(self, *, token: str, db_path: Path) -> None:
        self.token = token
        self.db_path = db_path

    async def load(self) -> None:
        async with Bot(
            token=self.token,
            default=DefaultBotProperties(parse_mode="HTML"),
        ).context() as bot:
            await bot.set_my_commands(commands=self._get_commands())
            dp = Dispatcher(storage=self._get_storage())
            dp.include_routers(*self._get_routers())

            logger.info("Bot started")
            await dp.start_polling(bot)

    def _get_storage(self) -> BaseStorage:
        logger.debug(f"Creating memory storage")
        return MemoryStorage()

    @staticmethod
    def _get_routers() -> tuple[Router, ...]:
        routers = (main_router,)
        logger.debug(f"Loading {[r.name for r in routers]} routers")
        return routers

    @staticmethod
    def _get_commands() -> list[BotCommand]:
        return [
            BotCommand(command="/start", description="Запустить бота"),
            BotCommand(command="/about", description="О боте"),
            BotCommand(command="/help", description="Помощь"),
        ]
