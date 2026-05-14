from pydantic import BaseModel


class MenuNodeFlags(BaseModel):
    is_back: bool = True
    is_main: bool = True
    build: bool = True
