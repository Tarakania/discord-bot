import hmac
import json
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

    await notify_restart_started(
        req.app["bot"], commits_count=payload.get("size", -1)
    )


async def git_pull() -> None:
    print("[GIT] pull started")

    await run_subprocess_shell("git pull origin master")

    print("[GIT] pull completed")


async def notify_restart_started(
    bot: "TarakaniaRPG", commits_count: int = -1
) -> None:
    update_channel = bot.get_channel(UPDATE_CHANNEL_ID)

    message_base = "\N{INFORMATION SOURCE} Restarting bot to apply "
    if commits_count == -1:
        message = message_base + "updates"
    else:
        message = message_base + f"**{commits_count}** commits"

    await update_channel.send(message)


async def notify_restart_completed(bot: "TarakaniaRPG") -> None:
    update_channel = bot.get_channel(UPDATE_CHANNEL_ID)

    await update_channel.send(
        "\N{INFORMATION SOURCE} Bot successfully restarted"
    )


async def wait_clean_exit(app: web.Application) -> None:
    await git_pull()

    await app["runner"].cleanup()
    await app.cleanup()
    await app["bot"].logout()

    print("Successfully exited")


async def update_webhook(req: web.Request) -> web.Response:
    await verify_github_request(req)
    await parse_github_request(req)

    print("Update webhook fired")

    asyncio.create_task(wait_clean_exit(req.app))

    return web.Response()


async def start_updater(bot: "TarakaniaRPG") -> None:
    host = "0.0.0.0"
    port = 60000

    app = web.Application()

    app["bot"] = bot

    with open("config.json") as f:
        app["config"] = json.load(f)

    app.add_routes([web.post("/tarakania-rpg-bot-webhook", update_webhook)])

    runner = web.AppRunner(app)
    app["runner"] = runner

    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

    print(f"Listening for github events on port {port}")

    await notify_restart_completed(bot)
