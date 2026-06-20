class DomainError(Exception):
    pass


class NotFoundError(DomainError):
    pass


class ContentNotFoundError(NotFoundError):
    def __init__(self, file_name):
        super().__init__(f"Content not found: {file_name}")


class MediaNotFoundError(NotFoundError):
    def __init__(self, media_item):
        super().__init__(f"Media file not found: {media_item}")


class ButtonNotFoundError(NotFoundError):
    def __init__(self, button_label):
        super().__init__(f"Button not found: {button_label}")


class HistoryNotFoundError(NotFoundError):
    def __init__(self, user_key):
        super().__init__(f"History not found for user: {user_key}")


class CacheError(DomainError):
    pass


class CacheMissError(CacheError):
    def __init__(self, cache_key):
        super().__init__(f"Cache miss for key: {cache_key}")


class CacheExpiredError(CacheError):
    def __init__(self, cache_key):
        super().__init__(f"Cache expired for key: {cache_key}")


class ValidationError(DomainError):
    pass


class NotSupportedTypeError(ValidationError):
    def __init__(self, unexpected):
        super().__init__(f"Unsupported type: {unexpected}")


class MediaValidationError(ValidationError):
    pass


class NotSupportedKeyboardError(MediaValidationError):
    pass


class NotUniqueButtonsError(MediaValidationError):
    def __init__(self):
        super().__init__("Not unique buttons in keyboard")


class TooLongFieldError(MediaValidationError):
    pass


class VideoValidationError(MediaValidationError):
    pass
