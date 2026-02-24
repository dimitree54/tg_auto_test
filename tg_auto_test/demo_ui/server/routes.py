"""HTTP route handlers for the demo server."""

from pathlib import Path
from typing import TYPE_CHECKING  # noqa: TID251

from fastapi import FastAPI, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from telethon.tl.functions.bots import GetBotCommandsRequest, GetBotMenuButtonRequest
from telethon.tl.functions.messages import SendVoteRequest
from telethon.tl.functions.payments import SendStarsFormRequest
from telethon.tl.types import (
    BotCommandScopeDefault,
    BotMenuButtonCommands,
    InputInvoiceMessage,
    InputPeerEmpty,
    InputPeerUser,
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
from tg_auto_test.demo_ui.server.serialize import serialize_message
from tg_auto_test.demo_ui.server.upload_handlers import handle_file_upload

if TYPE_CHECKING:
    from tg_auto_test.demo_ui.server.demo_server import DemoServer


def register_routes(app: FastAPI, demo_server: "DemoServer", templates_dir: Path | None) -> None:
    """Register API routes on the FastAPI app."""

    @app.get("/")
    async def index() -> FileResponse:
        if templates_dir and (templates_dir / "index.html").exists():
            return FileResponse(templates_dir / "index.html")
        raise HTTPException(status_code=404, detail="Template not found")

    @app.get("/api/file/{file_id}")
    async def serve_file(file_id: str, download: int = 0) -> Response:
        file_data = demo_server.file_store.get(file_id)
        if file_data is None:
            raise HTTPException(status_code=404, detail="File not found")

        filename, content_type, data = file_data
        disposition = "attachment" if download else "inline"
        return Response(
            content=data,
            media_type=content_type,
            headers={"Content-Disposition": f'{disposition}; filename="{filename}"'},
        )

    @app.get("/api/state")
    async def get_state() -> BotStateResponse:
        # Get commands via TL request
        scope = BotCommandScopeDefault()
        commands = await demo_server.client(GetBotCommandsRequest(scope=scope, lang_code=""))
        command_list = [BotCommandInfo(command=cmd.command, description=cmd.description) for cmd in commands]

        # Get menu button via TL request
        menu_button = await demo_server.client(GetBotMenuButtonRequest(user_id=InputPeerUser(user_id=0, access_hash=0)))
        menu_type = "commands" if isinstance(menu_button, BotMenuButtonCommands) else "default"

        response = BotStateResponse(commands=command_list, menu_button_type=menu_type)

        if demo_server.on_action is not None:
            await demo_server.on_action("get_state", demo_server.client)

        return response

    @app.post("/api/message")
    async def send_message(req: TextMessageRequest) -> MessageResponse:
        async with demo_server.client.conversation(demo_server.peer, demo_server.timeout) as conv:
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
        # Create SendStarsFormRequest with InputInvoiceMessage
        request = SendStarsFormRequest(
            form_id=req.message_id,
            invoice=InputInvoiceMessage(peer=InputPeerEmpty(), msg_id=req.message_id),
        )
        # Execute the request via client
        await demo_server.client(request)
        response = demo_server.client._pop_response()  # noqa: SLF001
        result = await serialize_message(response, demo_server.file_store)

        if demo_server.on_action is not None:
            await demo_server.on_action("pay_stars", demo_server.client)

        return result

    @app.post("/api/callback")
    async def handle_callback(req: CallbackRequest) -> MessageResponse:
        # Use Telethon's standard button click API
        msg = await demo_server.client.get_messages(demo_server.peer, ids=req.message_id)
        if not msg:
            raise HTTPException(status_code=404, detail=f"Message {req.message_id} not found")

        # Click button and get response - ServerlessTelegramClient provides the response
        response = await msg.click(data=req.data.encode())
        result = await serialize_message(response, demo_server.file_store)

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
        demo_server = app.state.demo_server

        # Convert option indices to bytes (consistent with model_helpers.py)
        option_bytes = [bytes([i]) for i in request.option_ids]

        # Use Telethon SendVoteRequest pattern
        vote_request = SendVoteRequest(
            peer=InputPeerEmpty(),  # Ignored in serverless mode
            msg_id=request.message_id,
            options=option_bytes,
        )

        # Execute the request
        await demo_server.client(vote_request)

        # Get the response
        response = demo_server.client._pop_response()  # noqa: SLF001

        # Serialize the bot response
        result = await serialize_message(response, demo_server.file_store)

        # Call custom action callback if provided
        if demo_server.on_action is not None:
            await demo_server.on_action("poll_vote", demo_server.client)

        return result
