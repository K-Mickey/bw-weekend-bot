import logging
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramSettings(BaseSettings):
    bot_token: str = ""
    webhook_url: str = ""
    webhook_path: str = "/tg-webhook"
    webhook_secret: str = ""

    model_config = SettingsConfigDict(
        env_prefix="TELEGRAM_",
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )


class VKSettings(BaseSettings):
    bot_token: str = ""
    webhook_url: str = ""
    webhook_title: str = "bw-weekend-bot"
    webhook_path: str = "/vk-webhook"
    webhook_secret: str = ""

    model_config = SettingsConfigDict(
        env_prefix="VK_",
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )


class Settings(BaseSettings):
    base_dir: Path = Path(__file__).parent.parent
    content_dir: Path = base_dir / "content"
    content_data_dir: Path = content_dir / "data"
    test_data_dir: Path = base_dir / "tests" / "test_data"

    log_level: str = logging.INFO

    web_server_host: str = "0.0.0.0"
    web_server_port: int = 8000

    telegram: TelegramSettings = TelegramSettings()
    vk: VKSettings = VKSettings()

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
