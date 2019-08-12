from typing import Any, Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from parser.converters import Converter


class ParserError(Exception):
    pass


class TooManyArguments(ParserError):
    def __str__(self) -> str:
        return "Команде передано слишком много аргументов"


class TooFewArguments(ParserError):
    def __str__(self) -> str:
        return "Команде передано недостаточно аргументов"


class ConvertError(ParserError):
    def __init__(
        self,
        value: Any,
        converter: "Converter",
        message: str = "",
        original_exc: Optional[BaseException] = None,
    ) -> None:
        super().__init__(message)

        self.value = value
        self.converter = converter
        self.original_exc = original_exc
        self.message = message

    def __str__(self) -> str:
        if self.message:
            return self.message

        return f"Невозможно привести аргумент к типу **{self.converter.display_name}**"
