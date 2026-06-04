import re

from pydantic import BaseModel, Field, field_validator


class Video(BaseModel):
    local_path: str = Field(...)
    vk_url: str = Field(default="")
    description: str | None = None

    def __repr__(self):
        return f"VideoNode({self.local_path}, {self.vk_url}, {self.description})"

    @field_validator("description")
    @classmethod
    def check_description_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 1024:
            raise ValueError("description length must not exceed 1024 characters")
        return v

    @field_validator("vk_url")
    @classmethod
    def check_vk_url(cls, v: str) -> str:
        if not v:
            return v

        correct_urls = ("https://vkvideo.ru", "https://vk.com")
        if not any(v.startswith(url) for url in correct_urls):
            raise ValueError(f"vk_url must start with one of {correct_urls}")
        return v

    @property
    def vk_video_id(self) -> str:
        pattern = r"(?:video|clip)(-?\d+)_(\d+)"
        match = re.search(pattern, self.vk_url)
        if match:
            return match.group(0)
        else:
            raise ValueError("Не удалось извлечь ID видео из ссылки")
