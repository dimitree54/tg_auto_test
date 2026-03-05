"""File upload handlers for the demo server."""

from typing import TYPE_CHECKING  # noqa: TID251

from fastapi import UploadFile

from tg_auto_test.demo_ui.server.api_models import MessageResponse
from tg_auto_test.demo_ui.server.response_drain import drain_and_serialize

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
) -> list[MessageResponse]:
    """Handle file upload for any media type."""
    data = await file.read()

    async with demo_server.client.conversation(demo_server.peer, timeout=demo_server.timeout) as conv:
        # Send bytes directly using Telethon API
        await conv.send_file(
            data,
            caption=caption,
            force_document=force_document,
            voice_note=voice_note,
            video_note=video_note,
        )
        return await drain_and_serialize(conv, demo_server.file_store)
