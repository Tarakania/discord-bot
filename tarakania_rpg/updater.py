import ssl
import hmac
import asyncio
import logging

from typing import TYPE_CHECKING

from aiohttp import web

from cli import args
from utils.subprocess import run_subprocess_shell

if TYPE_CHECKING:
    from bot import TarakaniaRPG


UPDATE_CHANNEL_ID = 605063135526912010


log = logging.getLogger(__name__)
git_log = logging.getLogger(f"{__name__}.git")


async def verify_github_request(req: web.Request) -> None:
    header_signature = req.headers.get("X-Hub-Signature")
    if not header_signature:
        raise web.HTTPUnauthorized(reason="Missing signature header")

    secret = req.app["config"]["github-webhook-token"]

    sha_name, delim, signature = header_signature.partition("=")
    if not (sha_name or delim or signature):
        raise web.HTTPUnauthorized(reason="Bad signature header")

    mac = hmac.new(secret.encode(), msg=await req.read(), digestmod="sha1")

    if not hmac.compare_digest(mac.hexdigest(), signature):
        raise web.HTTPUnauthorized(reason="Hashes did not match")


async def parse_github_request(req: web.Request) -> None:
    payload = await req.json()

    # TODO: compare refs, iterate over commits and decide if restart is needed

    commits_count = payload.get("size", -1)
    if commits_count == -1:
        commits_count = len(payload.get("commits", [])) or -1

    await notify_restart_started(req.app["bot"], commits_count=commits_count)


async def git_pull() -> None:
    git_log.info("Pull started")

    if args.production:
        await run_subprocess_shell("git fetch --all")
        await run_subprocess_shell("git reset --hard origin/master")
    else:
        await run_subprocess_shell("git pull origin master")

    git_log.info("Pull completed")


async def notify_restart_started(bot: "TarakaniaRPG", commits_count: int = -1) -> None:
    if not args.enable_notifications:
        return

    update_channel = bot.get_channel(UPDATE_CHANNEL_ID)

    message_base = "\N{INFORMATION SOURCE} Перезагрузка бота для применения "
    if commits_count == -1:
        shutdown_message = message_base + "обновлений"
    else:
        shutdown_message = message_base + f"**{commits_count}** коммитов"

    try:
        await update_channel.send(shutdown_message)
    except Exception as e:
        log.warning(f"Failed to deliver notification: {shutdown_message}. Error: {e}")


async def notify_boot_completed(bot: "TarakaniaRPG") -> None:
    if not args.enable_notifications:
        return

    update_channel = bot.get_channel(UPDATE_CHANNEL_ID)

    boot_message = "\N{INFORMATION SOURCE} Бот успешно авторизировался"

    if not args.production:
        boot_message += "\n\N{WARNING SIGN} Работаю в режиме отладки"

    try:
        await update_channel.send(boot_message)
    except Exception as e:
        log.warning(f"Failed to deliver notification: {boot_message}. Error: {e}")


async def wait_clean_exit(app: web.Application) -> None:
    await git_pull()

    await app["runner"].cleanup()
    await app.cleanup()
    await app["bot"].logout()

    log.info("Successfully exited")


async def update_webhook_endpoint(req: web.Request) -> web.Response:
    await verify_github_request(req)
    await parse_github_request(req)

    log.debug("Update webhook fired")

    asyncio.create_task(wait_clean_exit(req.app))

    return web.Response()


async def start_updater(bot: "TarakaniaRPG") -> None:
    if not args.enable_updater:
        return

    app = web.Application()

    app["bot"] = bot
    app["config"] = bot.config

    app.add_routes([web.post("/tarakania-rpg-bot-webhook", update_webhook_endpoint)])

    runner = web.AppRunner(app)
    app["runner"] = runner

    await runner.setup()

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    updater_section = app["config"]["updater"]
    ssl_context.load_cert_chain(
        updater_section["cert-chain-path"], updater_section["cert-privkey-path"]
    )

    site = web.TCPSite(runner, args.wh_host, args.wh_port, ssl_context=ssl_context)
    await site.start()

    log.info(f"Listening for github events on port {args.wh_port}")

    await notify_boot_completed(bot)
