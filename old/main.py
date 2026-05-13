import argparse
import asyncio
import logging

from bot import start_polling, start_webhook
from settings import settings

if __name__ == "__main__":
    logging.basicConfig(
        level=settings.log_level,
        format=settings.log_format,
    )

    parser = argparse.ArgumentParser(description="Bot for budget")
    parser.add_argument("--local", action="store_true", default=False, help="Run bot in local mode")
    args = parser.parse_args()

    paths = (settings.log_path,)
    for path in paths:
        path.mkdir(exist_ok=True, parents=True)

    if args.local:
        asyncio.run(start_polling())

    else:
        start_webhook()
