from src.infrastructure.file_cache.value_objects.cache_key import CacheKey


class MediaCacheError(BaseException): ...


class MediaCacheMiss(MediaCacheError):
    def __init__(self, cache_key: CacheKey, *args):
        super().__init__(*args)
        self.message = f"Cache miss for key: {cache_key}"


class MediaCacheExpired(MediaCacheError):
    def __init__(self, cache_key: CacheKey, *args):
        super().__init__(*args)
        self.message = f"Cache expired for key: {cache_key}"
