from handler import BaseCommand, Context, Arguments, CommandResult

from rpg.player import Player, UnknownPlayer
from utils.confirmations import request_phrase_confirmation


CONFIRMATION_PHRASE = "Подтверждаю"


class Command(BaseCommand):
    async def run(self, ctx: Context, args: Arguments) -> CommandResult:
        try:
            player = await Player.from_id(ctx.author.id, self.bot.pg)
        except UnknownPlayer:
            return "У вас нет персонажа"

        confirmation_request = await ctx.send(
            f"Вы действительно хотите удалить персонажа **{player}**?\n"
            f"Это действие нельзя отменить.\n"
            f"Отправьте фразу **{CONFIRMATION_PHRASE}** для подтверждения"
        )

        if not await request_phrase_confirmation(
            ctx, confirmation_request, CONFIRMATION_PHRASE
        ):
            return await confirmation_request.edit(
                content="Вы не подтвердили удаление персонажа"
            )

        await player.delete(self.bot.pg)

        return await confirmation_request.edit(content="Ваш персонаж удалён")
