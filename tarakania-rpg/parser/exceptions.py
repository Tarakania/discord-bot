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
        argument: "Converter",
        *args: Any,
        original_exc: Optional[BaseException] = None,
    ) -> None:
        super().__init__(*args)

        self.value = value
        self.argument = argument
        self.original_exc = original_exc
