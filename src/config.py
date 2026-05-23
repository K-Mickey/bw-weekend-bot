from pathlib import Path

from pydantic_settings import BaseSettings


class TelegramSettings(BaseSettings):
    bot_token: str = ""
    webhook_url: str = ""
    webhook_path: str = "/webhook"
    webhook_secret: str = ""


class Settings(BaseSettings):
    base_dir: Path = Path(__file__).parent.parent
    content_dir: Path = base_dir / "content"
    content_data_dir: Path = content_dir / "data"
    test_data_dir: Path = base_dir / "tests" / "test_data"

    web_server_host: str = "0.0.0.0"
    web_server_port: int = 8000

    telegram: TelegramSettings = TelegramSettings()


settings = Settings()
