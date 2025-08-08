from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str

    base_path: Path = Path.cwd()
    db_path: Path = base_path / "src/bot.sqlite3"
    img_path: Path = base_path / "src/images"
    video_path: Path = base_path / "src/videos"

    log_level: str = "DEBUG"
    log_format: str = "[%(asctime)s] [%(levelname)s] [%(name)s - %(filename)s] > %(lineno)d - %(message)s"
    log_path: Path = base_path / "src/logs"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def user_ids(self) -> list[int]:
        return [int(x) for x in self.user_str_ids.split(",")]


settings = Settings()
