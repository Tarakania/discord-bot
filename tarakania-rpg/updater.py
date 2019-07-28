import hmac
import json
import asyncio

from typing import TYPE_CHECKING
from aiohttp import web


if TYPE_CHECKING:
    from bot import TarakaniaRPG


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


async def wait_clean_exit(app: web.Application) -> None:
    print("Exiting in 5 seconds")

    await asyncio.sleep(5)

    await app["runner"].cleanup()
    await app.cleanup()
    await app["bot"].logout()

    print("Successfully exited")


async def update_webhook(req: web.Request) -> web.Response:
    await verify_github_request(req)

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
