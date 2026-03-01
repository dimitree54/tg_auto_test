"""HTTP route handlers for the demo server."""

from pathlib import Path
import time
from typing import TYPE_CHECKING, Any, cast  # noqa: TID251

from fastapi import FastAPI, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, Response
from telethon.tl.functions.bots import GetBotCommandsRequest, GetBotMenuButtonRequest
from telethon.tl.types import (
    BotCommandScopeDefault,
    BotMenuButtonCommands,
)

from tg_auto_test.demo_ui.server.api_models import (
    BotCommandInfo,
    BotStateResponse,
    CallbackRequest,
    InvoicePayRequest,
    MessageResponse,
    PollVoteRequest,
    TextMessageRequest,
)
from tg_auto_test.demo_ui.server.file_store import build_file_response
from tg_auto_test.demo_ui.server.routes_interactive import (
    handle_callback as handle_callback_interactive,
    handle_pay_invoice,
    handle_poll_vote,
)
from tg_auto_test.demo_ui.server.serialize import serialize_message
from tg_auto_test.demo_ui.server.upload_handlers import handle_file_upload
from tg_auto_test.test_utils.exceptions import BotNoResponseError

if TYPE_CHECKING:
    from tg_auto_test.demo_ui.server.demo_server import DemoServer

_STARTUP_TS = str(int(time.time()))


def register_routes(app: FastAPI, demo_server: "DemoServer", templates_dir: Path | None) -> None:
    """Register API routes on the FastAPI app."""

    @app.exception_handler(BotNoResponseError)
    def _handle_bot_no_response(_request: Request, exc: BotNoResponseError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.get("/")
    async def index() -> HTMLResponse:
        if not templates_dir or not (templates_dir / "index.html").exists():
            raise HTTPException(status_code=404, detail="Template not found")
        html = (templates_dir / "index.html").read_text()
        html = html.replace("app.js", f"app.js?v={_STARTUP_TS}")
        html = html.replace("app.css", f"app.css?v={_STARTUP_TS}")
        return HTMLResponse(html)

    @app.get("/api/file/{file_id}")
    async def serve_file(file_id: str, download: int = 0) -> Response:
        return build_file_response(demo_server.file_store, file_id, download=bool(download))

    @app.get("/api/state")
    async def get_state() -> BotStateResponse:
        # Get commands via TL request
        scope = BotCommandScopeDefault()
        commands = await demo_server.client(GetBotCommandsRequest(scope=scope, lang_code=""))
        command_list = [BotCommandInfo(command=cmd.command, description=cmd.description) for cmd in cast(Any, commands)]

        # Get menu button via TL request with resolved peer
        user_id = await demo_server.client.get_input_entity(demo_server.peer)
        menu_button = await demo_server.client(GetBotMenuButtonRequest(user_id=cast(Any, user_id)))
        menu_type = "commands" if isinstance(menu_button, BotMenuButtonCommands) else "default"

        response = BotStateResponse(commands=command_list, menu_button_type=menu_type)

        if demo_server.on_action is not None:
            await demo_server.on_action("get_state", demo_server.client)

        return response

    @app.post("/api/message")
    async def send_message(req: TextMessageRequest) -> MessageResponse:
        async with demo_server.client.conversation(demo_server.peer, timeout=demo_server.timeout) as conv:
            await conv.send_message(req.text)
            response = await conv.get_response()
        result = await serialize_message(response, demo_server.file_store)

        if demo_server.on_action is not None:
            await demo_server.on_action("send_message", demo_server.client)

        return result

    @app.post("/api/document")
    async def send_document(file: UploadFile) -> MessageResponse:
        result = await handle_file_upload(demo_server, file, force_document=True)

        if demo_server.on_action is not None:
            await demo_server.on_action("send_file", demo_server.client)

        return result

    @app.post("/api/voice")
    async def send_voice(file: UploadFile) -> MessageResponse:
        result = await handle_file_upload(demo_server, file, voice_note=True)

        if demo_server.on_action is not None:
            await demo_server.on_action("send_file", demo_server.client)

        return result

    @app.post("/api/photo")
    async def send_photo(file: UploadFile, caption: str = Form("")) -> MessageResponse:
        result = await handle_file_upload(demo_server, file, caption=caption)

        if demo_server.on_action is not None:
            await demo_server.on_action("send_file", demo_server.client)

        return result

    @app.post("/api/video_note")
    async def send_video_note(file: UploadFile) -> MessageResponse:
        result = await handle_file_upload(demo_server, file, video_note=True)

        if demo_server.on_action is not None:
            await demo_server.on_action("send_file", demo_server.client)

        return result

    @app.post("/api/invoice/pay")
    async def pay_invoice(req: InvoicePayRequest) -> MessageResponse:
        result = await handle_pay_invoice(demo_server, req)
        if demo_server.on_action is not None:
            await demo_server.on_action("pay_stars", demo_server.client)
        return result

    @app.post("/api/callback")
    async def handle_callback(req: CallbackRequest) -> MessageResponse:
        result = await handle_callback_interactive(demo_server, req)
        if demo_server.on_action is not None:
            await demo_server.on_action("click_button", demo_server.client)
        return result

    @app.post("/api/reset")
    async def reset() -> dict[str, str]:
        # Clear file store
        demo_server.file_store.clear()

        # Reconnect client using Telethon interface
        await demo_server.client.disconnect()
        await demo_server.client.connect()

        # Call custom action callback if provided
        if demo_server.on_action is not None:
            await demo_server.on_action("reset", demo_server.client)

        return {"status": "ok"}

    @app.post("/api/poll/vote")
    async def vote_poll(request: PollVoteRequest) -> MessageResponse:
        """Handle poll vote by calling Telethon SendVoteRequest."""
        result = await handle_poll_vote(demo_server, request)
        if demo_server.on_action is not None:
            await demo_server.on_action("poll_vote", demo_server.client)
        return result
