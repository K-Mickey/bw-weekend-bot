def content_factory(raw: dict):
    match raw:
        case {"posts": _}:
            from src.domain.aggregates import PostGroup

            return PostGroup(**raw)
        case {"media": _}:
            from src.domain.aggregates import Post

            return Post(**raw)
        case _:
            raise ValueError("Invalid node")
