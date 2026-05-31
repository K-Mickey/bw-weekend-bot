from typing import Iterator

from pydantic import BaseModel, Field, field_validator, model_validator

from src.domain.value_objects.button import ButtonType


class KeyboardButton(BaseModel):
    text: str = Field(...)
    target: str = Field(...)
    type: ButtonType = Field(ButtonType.DEFAULT)

    @field_validator("text")
    @classmethod
    def truncate_long_text(cls, v: str) -> str:
        if len(v) > 35:
            return f"{v[:32]}..."
        return v


class KeyboardRow(BaseModel):
    buttons: list[KeyboardButton] = Field(...)

    def __iter__(self) -> Iterator[KeyboardButton]:
        return iter(self.buttons)

    def __getitem__(self, index) -> KeyboardButton:
        return self.buttons[index]


class Keyboard(BaseModel):
    rows: list[KeyboardRow] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_input(cls, values):
        if isinstance(values, list) and all(isinstance(row, list) for row in values):
            return {"rows": [{"buttons": row} for row in values]}

        return values

    @model_validator(mode="after")
    def check_unique_buttons(self) -> list[KeyboardRow]:
        buttons = [button.text for row in self.rows for button in row]
        if len(buttons) != len(set(buttons)):
            raise ValueError("Duplicate buttons in keyboard")
        return self

    def __iter__(self) -> Iterator[KeyboardRow]:
        return iter(self.rows)

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index) -> KeyboardRow:
        return self.rows[index]

    def add_row(self, row: KeyboardRow):
        self.rows.append(row)
