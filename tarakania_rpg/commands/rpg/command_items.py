from rpg.items.item import _all_items_by_id

from command import BaseCommand, CommandResult
from argparser.arguments import Arguments
from context import Context
from utils.formatting import codeblock


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        items = [(id, item) for id, item in _all_items_by_id.items()]
        items.sort(key=lambda x: x[0])

        return codeblock(
            "\n".join(sorted(f"{id:>3} {item.name}" for id, item in items))
        )
