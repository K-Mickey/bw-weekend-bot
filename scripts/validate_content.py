import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, NamedTuple, Sequence

from src.config import settings
from src.domain.aggregates import Content, Post
from src.domain.exceptions import ContentNotFoundError, MediaNotFoundError
from src.domain.value_objects.button import ButtonType
from src.domain.value_objects.media import MediaGroup, MediaType, Photo, Video
from src.domain.value_objects.node import NodeName
from src.infrastructure.content_repository import LocalContentRepository


class Link(NamedTuple):
    file_name: str | Path
    target: str


@dataclass
class ValidStatistic:
    files: set[Path] = field(default_factory=set)
    button_links: set[Path] = field(default_factory=set)
    media_links: set[MediaType] = field(default_factory=set)

    invalid_files: list[str | Path] = field(default_factory=list)
    invalid_button_links: list[Link] = field(default_factory=list)
    invalid_media_links: list[Link] = field(default_factory=list)

    def add_file(self, file_name: str | Path):
        self.files.add(Path(file_name))

    def add_button_link(self, file_name: str | Path):
        self.button_links.add(Path(file_name))

    def add_media_link(self, file: MediaType):
        self.media_links.add(file)

    def add_invalid_file(self, file_name: str | Path):
        self.invalid_files.append(file_name)

    def add_invalid_button(self, file_name: str | Path, target: str):
        self.invalid_button_links.append(Link(file_name, target))

    def add_invalid_media(self, file_name: str | Path, media_name: str):
        self.invalid_media_links.append(Link(file_name, media_name))

    @property
    def has_errors(self) -> bool:
        return bool(self.invalid_files + self.invalid_button_links + self.invalid_media_links)

    def get_statistic(
        self,
        all_yaml_files: Sequence[Path],
        all_photos: Sequence[Path],
        all_videos: Sequence[Path],
    ) -> str:
        all_yaml_files = {file.relative_to(settings.content_data_dir).with_suffix("") for file in all_yaml_files}
        all_photos = {file.relative_to(settings.content_photo_dir) for file in all_photos}
        all_videos = {file.relative_to(settings.content_video_dir) for file in all_videos}

        photo_paths = {Path(p.local_path) for p in self.media_links if isinstance(p, Photo)}
        video_paths = {Path(v.local_path) for v in self.media_links if isinstance(v, Video)}
        statistic = [
            "-" * 20,
            "Amount of files in the directory:",
            f"- {len(all_yaml_files)} files",
            f"- {len(all_photos)} photos",
            f"- {len(all_videos)} videos",
            "",
            "The bot will use of them:",
            f"- {len(self.button_links)} files through buttons + some required files(main, help, error)",
            f"- {len(photo_paths)} photos",
            f"- {len(video_paths)} videos",
            "",
            "Invalid files:",
            f"- {len(self.invalid_files)} invalid files(syntax errors)",
            f"- {len(self.invalid_button_links)} invalid button links",
            f"- {len(self.invalid_media_links)} invalid media links",
            "-" * 20,
            "Files with syntax errors:",
            *[f"- {file}" for file in self.invalid_files],
            "",
            "Files with invalid button links:",
            *[f"- {file} -> {target}" for file, target in self.invalid_button_links],
            "",
            "Files with invalid media links:",
            *[f"- {file} -> {media}" for file, media in self.invalid_media_links],
            "-" * 20,
            "Unused files:",
            *[f"- {file}" for file in all_yaml_files - self.button_links],
            "Unused photos:",
            *[f"- {file}" for file in all_photos - photo_paths],
            "Unused videos:",
            *[f"- {file}" for file in all_videos - video_paths],
            "-" * 20,
        ]

        return "\n".join(statistic)


class Checker:
    def __init__(self):
        self.repository = LocalContentRepository()
        self.statistic: ValidStatistic | None = None

    def check_content(self, files: Iterable[str]) -> ValidStatistic:
        self.statistic = ValidStatistic()

        visit_line = [file for file in files]
        visited = set()

        while visit_line:
            file_name = visit_line.pop()
            if file_name in visited:
                continue

            visited.add(file_name)

            self.statistic.add_file(file_name)

            try:
                content = self.repository.get_content(file_name)
            except:  # noqa: E722
                self.statistic.add_invalid_file(file_name)
            else:
                self._analyze_content(content, file_name)

                posts = [content] if isinstance(content, Post) else content.posts
                for post in posts:
                    buttons = filter(lambda x: x.type == ButtonType.DEFAULT, post.keyboard.get_buttons())
                    visit_line += [button.target for button in buttons]

        return self.statistic

    def _analyze_content(self, content: Content, file_name: str | Path):
        invalid_media = self._check_content_media_links(content)
        for media in invalid_media:
            self.statistic.add_invalid_media(file_name, media)
        invalid_buttons = self._check_content_button_links(content)
        for button in invalid_buttons:
            self.statistic.add_invalid_button(file_name, button)

    def _check_content_media_links(self, content: Content) -> list[str]:
        invalid_media_files = []
        posts = [content] if isinstance(content, Post) else content.posts
        for post in posts:
            media = post.media if isinstance(post.media, MediaGroup) else [post.media]
            for media_item in media:
                if isinstance(media_item, MediaType):
                    self.statistic.add_media_link(media_item)
                    try:
                        self.repository.get_media_path(media_item)
                    except MediaNotFoundError:
                        invalid_media_files.append(media_item)

        return invalid_media_files

    def _check_content_button_links(self, content: Content) -> list[str]:
        invalid_button_links = []
        posts = [content] if isinstance(content, Post) else content.posts
        for post in posts:
            buttons = filter(lambda x: x.type == ButtonType.DEFAULT, post.keyboard.get_buttons())
            for button in buttons:
                target = button.target
                self.statistic.add_button_link(button.target)
                try:
                    self.repository.get_content_path(target)
                except ContentNotFoundError:
                    invalid_button_links.append(target)
        return invalid_button_links

    @staticmethod
    def get_all_files():
        data_dir = settings.content_data_dir
        files = sorted(data_dir.rglob("*.yaml"))
        return [file for file in files if file.is_file() and file.name != ".gitkeep"]

    @staticmethod
    def get_all_photos():
        photo_dir = settings.content_photo_dir
        files = sorted(photo_dir.rglob("*"))
        return [file for file in files if file.is_file() and file.name != ".gitkeep"]

    @staticmethod
    def get_all_videos():
        video_dir = settings.content_video_dir
        files = sorted(video_dir.rglob("*"))
        return [file for file in files if file.is_file() and file.name != ".gitkeep"]


def check_base_file_exist() -> list[str]:
    repository = LocalContentRepository()
    not_exist_files = []
    for file in NodeName:
        if not repository.get_content_path(file):
            not_exist_files.append(file)

    return not_exist_files


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
    )

    log = logging.getLogger(__name__)

    not_exist_files = check_base_file_exist()
    if not_exist_files:
        log.info(
            f"For correct work you need to create yaml files: "
            f"{', '.join(not_exist_files)} in {settings.content_data_dir}"
        )

    if NodeName.ROOT in not_exist_files:
        log.error("Root file is not found")
        return 1

    checker = Checker()
    statistic = checker.check_content([NodeName.ROOT])

    result = statistic.get_statistic(
        all_yaml_files=checker.get_all_files(),
        all_photos=checker.get_all_photos(),
        all_videos=checker.get_all_videos(),
    )
    log.info(result)

    if statistic.has_errors:
        return 1
    return 0


def run():
    sys.exit(main())


if __name__ == "__main__":
    run()
