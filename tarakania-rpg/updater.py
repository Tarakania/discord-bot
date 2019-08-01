import hmac
import asyncio

from typing import TYPE_CHECKING

from aiohttp import web

from utils.subprocess import run_subprocess_shell


if TYPE_CHECKING:
    from bot import TarakaniaRPG


UPDATE_CHANNEL_ID = 605063135526912010


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
    print("[GIT] pull started")

    await run_subprocess_shell("git pull origin master")

    print("[GIT] pull completed")


async def notify_restart_started(
    bot: "TarakaniaRPG", commits_count: int = -1
) -> None:
    if not bot.args.enable_notifications:
        return

    update_channel = bot.get_channel(UPDATE_CHANNEL_ID)

    message_base = "\N{INFORMATION SOURCE} Restarting bot to apply "
    if commits_count == -1:
        shutdown_message = message_base + "updates"
    else:
        shutdown_message = message_base + f"**{commits_count}** commits"

    try:
        await update_channel.send(shutdown_message)
    except Exception:
        print(f"Failed to deliver notification: {shutdown_message}")


async def notify_boot_completed(bot: "TarakaniaRPG") -> None:
    if not bot.args.enable_notifications:
        return

    update_channel = bot.get_channel(UPDATE_CHANNEL_ID)

    boot_message = "\N{INFORMATION SOURCE} Bot successfully lohgged in."

    if not bot.args.production:
        boot_message += "\n\N{WARNING SIGN} Working in debug mode."

    try:
        await update_channel.send(boot_message)
    except Exception:
        print(f"Failed to deliver notification: {boot_message}")


async def wait_clean_exit(app: web.Application) -> None:
    await git_pull()

    await app["runner"].cleanup()
    await app.cleanup()
    await app["bot"].logout()

    print("Successfully exited")


async def update_webhook_endpoint(req: web.Request) -> web.Response:
    await verify_github_request(req)
    await parse_github_request(req)

    print("Update webhook fired")

    asyncio.create_task(wait_clean_exit(req.app))

    return web.Response()


async def start_updater(bot: "TarakaniaRPG") -> None:
    app = web.Application()

    app["bot"] = bot
    app["config"] = bot.config

    app.add_routes(
        [web.post("/tarakania-rpg-bot-webhook", update_webhook_endpoint)]
    )

    runner = web.AppRunner(app)
    app["runner"] = runner

    await runner.setup()
    site = web.TCPSite(runner, bot.args.wh_host, bot.args.wh_port)
    await site.start()

    print(f"Listening for github events on port {bot.args.wh_port}")

    await notify_boot_completed(bot)
