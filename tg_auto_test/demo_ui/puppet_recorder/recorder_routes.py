"""Recording-aware chat API routes for the puppet recorder server."""

from typing import TYPE_CHECKING  # noqa: TID251

from fastapi import FastAPI, Form, HTTPException, UploadFile
from fastapi.responses import Response

from tg_auto_test.demo_ui.puppet_recorder.recorder_models import RecordedStep
from tg_auto_test.demo_ui.puppet_recorder.recorder_routes_control import register_recording_control_routes
from tg_auto_test.demo_ui.server.api_models import (
    CallbackRequest,
    MessageResponse,
    TextMessageRequest,
)
from tg_auto_test.demo_ui.server.file_store import build_file_response
from tg_auto_test.demo_ui.server.serialize import serialize_message
from tg_auto_test.demo_ui.server.upload_handlers import handle_file_upload

if TYPE_CHECKING:
    from tg_auto_test.demo_ui.puppet_recorder.recorder_server import PuppetRecorderServer


def register_recorder_routes(app: FastAPI, server: "PuppetRecorderServer") -> None:
    """Register all API routes with recording wrappers."""

    @app.get("/api/file/{file_id}")
    async def serve_file(file_id: str, download: int = 0) -> Response:
        return build_file_response(server.file_store, file_id, download=bool(download))

    @app.post("/api/message")
    async def send_message(req: TextMessageRequest) -> MessageResponse:
        async with server.client.conversation(server.peer, timeout=server.timeout) as conv:
            await conv.send_message(req.text)
            response = await conv.get_response()
        result = await serialize_message(response, server.file_store)
        server.session.add_step(
            RecordedStep(
                action="send_message",
                text=req.text,
                response_type=result.type,
                response_text=result.text,
                response_message_id=result.message_id,
            )
        )
        return result

    @app.post("/api/photo")
    async def send_photo(file: UploadFile, caption: str = Form("")) -> MessageResponse:
        result = await handle_file_upload(server, file, caption=caption)
        server.session.add_step(
            RecordedStep(
                action="send_file",
                file_type="photo",
                caption=caption,
                response_type=result.type,
                response_text=result.text,
                response_message_id=result.message_id,
            )
        )
        return result

    @app.post("/api/document")
    async def send_document(file: UploadFile) -> MessageResponse:
        result = await handle_file_upload(server, file, force_document=True)
        server.session.add_step(
            RecordedStep(
                action="send_file",
                file_type="document",
                response_type=result.type,
                response_text=result.text,
                response_message_id=result.message_id,
            )
        )
        return result

    @app.post("/api/voice")
    async def send_voice(file: UploadFile) -> MessageResponse:
        result = await handle_file_upload(server, file, voice_note=True)
        server.session.add_step(
            RecordedStep(
                action="send_file",
                file_type="voice",
                response_type=result.type,
                response_text=result.text,
                response_message_id=result.message_id,
            )
        )
        return result

    @app.post("/api/video_note")
    async def send_video_note(file: UploadFile) -> MessageResponse:
        result = await handle_file_upload(server, file, video_note=True)
        server.session.add_step(
            RecordedStep(
                action="send_file",
                file_type="video_note",
                response_type=result.type,
                response_text=result.text,
                response_message_id=result.message_id,
            )
        )
        return result

    @app.post("/api/callback")
    async def handle_callback(req: CallbackRequest) -> MessageResponse:
        msg = await server.client.get_messages(server.peer, ids=req.message_id)
        if not msg:
            raise HTTPException(status_code=404, detail=f"Message {req.message_id} not found")
        click_result = await msg.click(data=req.data.encode())
        result = await serialize_message(click_result, server.file_store)
        server.session.add_step(
            RecordedStep(
                action="click_button",
                callback_data=req.data,
                message_id=req.message_id,
                response_type=result.type,
                response_text=result.text,
                response_message_id=result.message_id,
            )
        )
        return result

    @app.post("/api/reset")
    async def reset() -> dict[str, str]:
        server.file_store.clear()
        await server.client.disconnect()
        await server.client.connect()
        return {"status": "ok"}

    register_recording_control_routes(app, server)
