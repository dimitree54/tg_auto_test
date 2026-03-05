"""HTTP route handlers for the demo server."""

from pathlib import Path
import time
from typing import TYPE_CHECKING, Any, cast  # noqa: TID251

from fastapi import FastAPI, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
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
    PollVoteRequest,
    TextMessageRequest,
)
from tg_auto_test.demo_ui.server.file_store import build_file_response
from tg_auto_test.demo_ui.server.serverless_route_actions import (
    stream_callback_action,
    stream_file_action,
    stream_payment_action,
    stream_poll_action,
    stream_text_action,
)
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
    async def send_message(req: TextMessageRequest, request: Request) -> StreamingResponse:
        return stream_text_action(demo_server, request, req.text)

    @app.post("/api/document")
    async def send_document(file: UploadFile, request: Request) -> StreamingResponse:
        data = await file.read()
        return stream_file_action(demo_server, request, data, force_document=True)

    @app.post("/api/voice")
    async def send_voice(file: UploadFile, request: Request) -> StreamingResponse:
        data = await file.read()
        return stream_file_action(demo_server, request, data, voice_note=True)

    @app.post("/api/photo")
    async def send_photo(file: UploadFile, request: Request, caption: str = Form("")) -> StreamingResponse:
        data = await file.read()
        return stream_file_action(demo_server, request, data, caption=caption)

    @app.post("/api/video_note")
    async def send_video_note(file: UploadFile, request: Request) -> StreamingResponse:
        data = await file.read()
        return stream_file_action(demo_server, request, data, video_note=True)

    @app.post("/api/invoice/pay")
    async def pay_invoice(req: InvoicePayRequest, request: Request) -> StreamingResponse:
        return stream_payment_action(demo_server, request, req.message_id)

    @app.post("/api/callback")
    async def handle_callback(req: CallbackRequest, request: Request) -> StreamingResponse:
        return stream_callback_action(demo_server, request, req.message_id, req.data)

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
    async def vote_poll(req: PollVoteRequest, request: Request) -> StreamingResponse:
        return stream_poll_action(demo_server, request, req.message_id, req.option_ids)
