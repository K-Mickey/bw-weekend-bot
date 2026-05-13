import secrets
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str

    webhook_url: str = "https://example.com/webhook"
    webhook_path: str = "/webhook"
    webhook_secret: str = secrets.token_urlsafe(32)
    web_server_host: str = "0.0.0.0"
    web_server_port: int = 8000

    redis_url: str = "redis://localhost:6379/0"

    base_path: Path = Path.cwd()
    img_path: Path = base_path / "src/images"
    video_path: Path = base_path / "src/videos"

    log_level: str = "DEBUG"
    log_format: str = "[%(asctime)s] [%(levelname)s] [%(name)s - %(filename)s] > %(lineno)d - %(message)s"
    log_path: Path = base_path / "src/logs"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
