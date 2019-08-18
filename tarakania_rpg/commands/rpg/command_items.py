from handler import BaseCommand, Context, Arguments, CommandResult

from rpg.items import Item
from rpg.rpg_object import all_instances
from utils.formatting import codeblock


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        items = [i for i in all_instances(Item)]
        items.sort(key=lambda x: x.id)

        return codeblock(
            "\n".join(sorted(f"{item.id:>3} {item.name}" for item in items))
        )
