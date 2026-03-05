"""File upload handlers for the demo server."""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING  # noqa: TID251

from fastapi import UploadFile
from fastapi.responses import StreamingResponse

from tg_auto_test.demo_ui.server.api_models import MessageResponse
from tg_auto_test.demo_ui.server.response_drain import drain_and_serialize, drain_sse_events

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
    """Handle file upload for any media type (batch, used by puppet recorder)."""
    data = await file.read()

    async with demo_server.client.conversation(demo_server.peer, timeout=demo_server.timeout) as conv:
        await conv.send_file(
            data,
            caption=caption,
            force_document=force_document,
            voice_note=voice_note,
            video_note=video_note,
        )
        return await drain_and_serialize(conv, demo_server.file_store)


async def stream_file_upload(
    demo_server: "DemoServer",
    file: UploadFile,
    *,
    caption: str = "",
    force_document: bool = False,
    voice_note: bool = False,
    video_note: bool = False,
) -> StreamingResponse:
    """Handle file upload with SSE streaming responses."""
    data = await file.read()

    async def _stream() -> AsyncIterator[str]:
        async with demo_server.client.conversation(demo_server.peer, timeout=demo_server.timeout) as conv:
            await conv.send_file(
                data,
                caption=caption,
                force_document=force_document,
                voice_note=voice_note,
                video_note=video_note,
            )
            async for chunk in drain_sse_events(conv, demo_server.file_store):
                yield chunk
        if demo_server.on_action is not None:
            await demo_server.on_action("send_file", demo_server.client)

    return StreamingResponse(_stream(), media_type="text/event-stream")
