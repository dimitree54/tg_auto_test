"""File upload handlers for the demo server."""

from typing import TYPE_CHECKING  # noqa: TID251

from fastapi import UploadFile

from tg_auto_test.demo_ui.server.api_models import MessageResponse
from tg_auto_test.demo_ui.server.serialize import store_response_file

if TYPE_CHECKING:
    from tg_auto_test.demo_ui.server.demo_server import DemoServer


async def handle_file_upload(
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

    async with demo_server.client.conversation(demo_server.peer, timeout=demo_server.timeout) as conv:
        # Send bytes directly using Telethon API
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
