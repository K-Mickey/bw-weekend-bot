from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    base_dir: Path = Path(__file__).parent.parent

    content_dir: Path = base_dir / "content"
    content_data_dir: Path = content_dir / "data"

    test_content_dir: Path = base_dir / "tests" / "test_data" / "content"
    test_content_data_dir: Path = test_content_dir / "data"

    bot_token_telegram: str = ""

    webhook_url: str = ""
    webhook_path: str = "/webhook"
    webhook_secret: str = ""
    web_server_host: str = "0.0.0.0"
    web_server_port: int = 8000


settings = Settings()
