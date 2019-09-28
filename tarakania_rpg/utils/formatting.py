from typing import Any, List


def codeblock(string: str, language: str = "") -> str:
    """Wrap string in codeblock"""

    return f"```{language}\n{string}```"


"""https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/utils/formats.py"""


class TabularData:
    def __init__(self) -> None:
        self._widths: List[Any] = []
        self._columns: List[Any] = []
        self._rows: List[Any] = []

    def set_columns(self, columns: List[str]) -> None:
        self._columns = columns
        self._widths = [len(c) + 2 for c in columns]

    def add_row(self, row: List[Any]) -> None:
        rows = [str(r) for r in row]
        self._rows.append(rows)
        for index, element in enumerate(rows):
            width = len(element) + 1
            if width > self._widths[index]:
                self._widths[index] = width

    def add_rows(self, rows: List[Any]) -> None:
        for row in rows:
            self.add_row(list(row))

    def render(self) -> str:
        """Renders a table in rST format.
        Example:
        +-------+-----+
        | Name  | Age |
        +-------+-----+
        | Alice | 24  |
        |  Bob  | 19  |
        +-------+-----+
        """

        sep = "+".join("-" * w for w in self._widths)
        sep = f"+{sep}+"

        to_draw = [sep]

        def get_entry(d: List[Any]) -> str:
            elem = "|".join(f"{e:^{self._widths[i]}}" for i, e in enumerate(d))
            return f"|{elem}|"

        to_draw.append(get_entry(self._columns))
        to_draw.append(sep)

        for row in self._rows:
            to_draw.append(get_entry(row))

        to_draw.append(sep)
        return "\n".join(to_draw)
