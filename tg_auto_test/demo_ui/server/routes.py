"""HTTP route handlers for the demo server."""

from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response

from tg_auto_test.demo_ui.server.api_models import (
    BotCommandInfo,
    BotStateResponse,
    CallbackRequest,
    InvoicePayRequest,
    MessageResponse,
    TextMessageRequest,
)
from tg_auto_test.demo_ui.server.serialize import serialize_message, store_response_file


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
        if not demo_server.backend.supports_capability("bot_state"):
            return BotStateResponse(commands=[], menu_button_type="default")

        commands_data, menu_type = await demo_server.backend.get_bot_state()
        commands = [BotCommandInfo(**cmd) for cmd in commands_data]
        return BotStateResponse(commands=commands, menu_button_type=menu_type)

    @app.post("/api/message")
    async def send_message(req: TextMessageRequest) -> MessageResponse:
        async with demo_server.backend.conversation(demo_server.peer, demo_server.timeout) as conv:
            await conv.send_message(req.text)
            response = await conv.get_response()
        return await serialize_message(response, demo_server.file_store)

    @app.post("/api/document")
    async def send_document(file: UploadFile) -> MessageResponse:
        return await _handle_file_upload(demo_server, file, force_document=True)

    @app.post("/api/voice")
    async def send_voice(file: UploadFile) -> MessageResponse:
        return await _handle_file_upload(demo_server, file, voice_note=True)

    @app.post("/api/photo")
    async def send_photo(file: UploadFile, caption: str = Form("")) -> MessageResponse:
        return await _handle_file_upload(demo_server, file, caption=caption)

    @app.post("/api/video_note")
    async def send_video_note(file: UploadFile) -> MessageResponse:
        return await _handle_file_upload(demo_server, file, video_note=True)

    @app.post("/api/invoice/pay")
    async def pay_invoice(req: InvoicePayRequest) -> MessageResponse:
        if not demo_server.backend.supports_capability("invoice_payments"):
            raise HTTPException(status_code=501, detail="Invoice payments not supported by this backend")

        response = await demo_server.backend.handle_invoice_payment(req.message_id)
        return await serialize_message(response, demo_server.file_store)

    @app.post("/api/callback")
    async def handle_callback(req: CallbackRequest) -> MessageResponse:
        if not demo_server.backend.supports_capability("callback_queries"):
            raise HTTPException(status_code=501, detail="Callback queries not supported by this backend")

        response = await demo_server.backend.handle_callback(demo_server.peer, req.message_id, req.data)
        return await serialize_message(response, demo_server.file_store)

    @app.post("/api/reset")
    async def reset() -> dict[str, str]:
        # Clear file store
        demo_server.file_store.clear()

        # Reconnect if managing lifecycle
        if demo_server.backend.manage_lifecycle:
            await demo_server.backend.disconnect()
            await demo_server.backend.connect()

        return {"status": "ok"}


async def _handle_file_upload(
    demo_server: "DemoServer",
    file: UploadFile,
    *,
    caption: str = "",
    force_document: bool = False,
    voice_note: bool = False,
    video_note: bool = False,
) -> MessageResponse:
    """Handle file upload for any media type."""
    data = await file.read()
    filename = file.filename or "file"
    content_type = file.content_type or "application/octet-stream"

    async with demo_server.backend.conversation(demo_server.peer, demo_server.timeout) as conv:
        # Send bytes directly - backends handle the conversion
        await conv.send_file(
            data,
            caption=caption,
            force_document=force_document,
            voice_note=voice_note,
            video_note=video_note,
        )
        response = await conv.get_response()

    # Determine response file type
    response_type = "document"
    if voice_note:
        response_type = "voice"
    elif video_note:
        response_type = "video_note"
    elif not force_document and content_type.startswith("image/"):
        response_type = "photo"

    file_id = response.response_file_id or filename
    stored_filename = await store_response_file(file_id, response, demo_server.file_store, filename, content_type, data)

    return MessageResponse(
        type=response_type,
        file_id=file_id,
        filename=stored_filename,
        message_id=response.id,
    )
