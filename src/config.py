from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    base_dir: Path = Path(__file__).parent.parent

    content_dir: Path = base_dir / "content"
    content_data_dir: Path = content_dir / "data"


settings = Settings()
