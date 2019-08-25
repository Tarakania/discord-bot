from handler import Context, Arguments, CommandResult

from utils.command_helpers import get_author_player
from utils.confirmations import request_phrase_confirmation


CONFIRMATION_PHRASE = "Подтверждаю"


async def run(ctx: Context, args: Arguments) -> CommandResult:
    player = await get_author_player(ctx)

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

    await player.delete(ctx.bot.pg)

    return await confirmation_request.edit(content="Ваш персонаж удалён")
