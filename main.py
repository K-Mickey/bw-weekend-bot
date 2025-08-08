import asyncio
import logging

from bot import BuBot
from settings import settings

if __name__ == "__main__":
    logging.basicConfig(
        level=settings.log_level,
        format=settings.log_format,
    )

    paths = (settings.log_path,)
    for path in paths:
        path.mkdir(exist_ok=True, parents=True)

    asyncio.run(
        BuBot(
            token=settings.bot_token,
            db_path=settings.db_path,
        ).load()
    )
