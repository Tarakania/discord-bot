from itertools import zip_longest
from typing import Any, List, Union, Iterator, Optional, overload

from context import Context
from argparser.converters import Converter
from argparser.exceptions import (
    TooFewArguments,
    TooManyArguments,
    ConvertError,
)


class Arguments:
    def __init__(self, content: str):
        # TODO: better splitter (shlex?)
        # TODO: flags support?
        self._args: List[str] = content.split()
        self._converted: List[Any] = []

    async def convert(self, ctx: Context, converters: List[Converter]) -> None:
        actual_values = []
        actual_converters: List[Converter] = []

        for i, (value, converter) in enumerate(
            zip_longest(self._args[1:], converters)
        ):
            if value is None:  # arguments exausted
                if not converter.optional:
                    raise TooFewArguments

                if converter.default_value is None:
                    continue

                actual_values.append(converter.default_value)
            else:
                actual_values.append(value)

            if converter is None:  # converters exausted
                if i == 0:
                    raise TooManyArguments

                last_converter = actual_converters[i - 1]

                if not last_converter.greedy:
                    raise TooManyArguments

                actual_converters.append(last_converter)

            else:
                actual_converters.append(converter)

        for value, converter in zip(actual_values, actual_converters):
            try:
                converted = await converter.convert(ctx, value)
            except ConvertError:
                raise
            except Exception as e:
                raise ConvertError(value, converter, original_exc=e)

            self._converted.append(converted)

    @property
    def command(self) -> Optional[str]:
        return self._args[0].lower() if len(self._args) else None

    def __len__(self) -> int:
        return len(self._args) - 1

    def __bool__(self) -> bool:
        return len(self._args) > 1

    def __repr__(self) -> str:
        return f"<Arguments command={self.command}>"

    @overload
    def __getitem__(self, value: int) -> Any:
        ...

    @overload  # noqa: F811
    def __getitem__(self, value: slice) -> List[Any]:
        ...

    def __getitem__(  # noqa: F811
        self, index: Union[int, slice]
    ) -> Union[Any, List[Any]]:
        if len(self._args) - len(self._converted) != 1:
            raise RuntimeError(
                "Bad number of converted values. Was 'convert' called?"
            )

        if isinstance(index, int):
            return self._converted[index]

        if index.step is not None:
            raise ValueError("Slicing with step is not supported")

        return self._converted[index]

    def __iter__(self) -> Iterator[Any]:
        yield from self._converted
