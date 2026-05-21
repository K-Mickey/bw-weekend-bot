from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    base_dir: Path = Path(__file__).parent.parent

    content_dir: Path = base_dir / "content"
    content_data_dir: Path = content_dir / "data"

    BOT_TOKEN_TELEGRAM: str = ""

    # Webhook configuration (optional)
    WEBHOOK_URL: str = ""
    WEBHOOK_PATH: str = "/webhook"
    WEBHOOK_SECRET: str = ""
    WEB_SERVER_HOST: str = "0.0.0.0"
    WEB_SERVER_PORT: int = 8000


settings = Settings()
