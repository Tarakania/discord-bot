from yaml import safe_load

from command import BaseCommand, CommandResult
from argparser.arguments import Arguments
from context import Context

from rpg.items.item import Item


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        item = args[0]

        items_data = Item._read_objects_from_file(item.__class__)
        item_data = items_data.get(item.id)

        if item_data is None:
            return "Предмет с таким id не найден в файле конфига"

        add_attribute = False
        del_attribute = False

        attributes = args[1].lower()
        if attributes.startswith("+"):
            attributes = attributes[1:]
            add_attribute = True
        elif attributes.startswith("-"):
            attributes = attributes[1:]
            del_attribute = True

        attribute_chain = attributes.split(".")
        current_level = item_data
        for attribute in attribute_chain[:-1]:
            try:
                current_level = current_level[attribute]
            except KeyError:
                if add_attribute:
                    current_level[attribute] = {}
                    current_level = current_level[attribute]
                    continue

                return f"Атрибут `{attribute}` не найден. Доступные атрибуты: **{', '.join(a for a in current_level)}**"

        if attribute_chain[-1] not in current_level:
            return f"Атрибут `{attribute_chain[-1]}` не найден. Доступные атрибуты: **{', '.join(a for a in current_level)}**"

        if del_attribute:
            del current_level[attribute_chain[-1]]
        else:
            if len(args) == 2:
                return "Необходим аргумент со значением"

            current_level[attribute_chain[-1]] = safe_load(args[2])

        new_item = item.from_data(item_data)

        # inject new item
        del new_item._all_items_by_id[item.id]
        del new_item._all_items_by_name[item.name.lower()]

        new_item._all_items_by_id[new_item.id] = new_item
        new_item._all_items_by_name[new_item.name.lower()] = new_item

        return f"Предмет: **{new_item!r}**\nЗначения: **{item_data}**"
