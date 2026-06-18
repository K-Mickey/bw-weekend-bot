from enum import StrEnum


class NodeName(StrEnum):
    ROOT = "main"
    HELP = "help"
    ERROR = "error"


class NodeKind(StrEnum):
    PHOTO = "photo"
    VIDEO = "video"
    TEXT = "text"
    POST = "post"
    POST_GROUP = "post_group"
