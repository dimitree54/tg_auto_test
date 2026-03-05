"""Coordinate concurrent handler execution with SSE streaming for demo routes."""

import asyncio
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING  # noqa: TID251

from fastapi.responses import StreamingResponse

from tg_auto_test.demo_ui.server.file_store import FileStore
from tg_auto_test.demo_ui.server.response_drain import stream_sse_from_queue
from tg_auto_test.test_utils.file_processing_utils import build_file_message_payload, process_file_message_data
from tg_auto_test.test_utils.models import ServerlessMessage
from tg_auto_test.test_utils.streaming_processor import _SENTINEL, run_handler_streaming

if TYPE_CHECKING:
    from tg_auto_test.demo_ui.server.demo_server import DemoServer


async def _run_text_streaming(
    demo_server: "DemoServer",
    text: str,
    queue: "asyncio.Queue[ServerlessMessage | object]",
) -> None:
    """Prepare a text message payload and run the handler, streaming responses."""
    client = demo_server.client
    client._outbox.clear()  # noqa: SLF001
    payload, msg = client._helpers.base_message_update(client._chat_id)  # noqa: SLF001
    msg["text"] = text
    if text.startswith("/"):
        msg["entities"] = [{"offset": 0, "length": text.find(" ") if " " in text else len(text), "type": "bot_command"}]
    await run_handler_streaming(client, payload, queue)


async def _run_file_streaming(
    demo_server: "DemoServer",
    data: bytes,
    queue: "asyncio.Queue[ServerlessMessage | object]",
    *,
    caption: str = "",
    force_document: bool = False,
    voice_note: bool = False,
    video_note: bool = False,
) -> None:
    """Prepare a file message payload and run the handler, streaming responses."""
    client = demo_server.client
    client._outbox.clear()  # noqa: SLF001
    file_id = client._helpers.make_file_id()  # noqa: SLF001
    file_bytes, _fname, _ct, file_data_obj = process_file_message_data(
        data, caption=caption, force_document=force_document, voice_note=voice_note, video_note=video_note
    )
    client._request.file_store[file_id] = file_data_obj  # noqa: SLF001
    payload, msg = client._helpers.base_message_update(client._chat_id)  # noqa: SLF001
    build_file_message_payload(payload, msg, file_id, data, file_bytes, caption, force_document, voice_note, video_note)
    await run_handler_streaming(client, payload, queue)


async def _run_with_sentinel(
    coro: object,
    queue: "asyncio.Queue[ServerlessMessage | object]",
) -> None:
    """Run *coro* and guarantee a sentinel lands on *queue* even on crash."""
    try:
        await coro  # type: ignore[misc]
    except Exception:
        queue.put_nowait(_SENTINEL)
        raise


def _make_sse_stream(
    handler_coro: object,
    queue: "asyncio.Queue[ServerlessMessage | object]",
    file_store: FileStore,
) -> AsyncIterator[str]:
    """Create an async iterator that runs a handler task and yields SSE events."""

    async def _stream() -> AsyncIterator[str]:
        task = asyncio.create_task(_run_with_sentinel(handler_coro, queue))  # type: ignore[arg-type]
        try:
            async for chunk in stream_sse_from_queue(queue, file_store):
                yield chunk
        finally:
            await task

    return _stream()


def stream_text_message(demo_server: "DemoServer", text: str) -> StreamingResponse:
    """Send a text message and return an SSE ``StreamingResponse``."""
    queue: asyncio.Queue[ServerlessMessage | object] = asyncio.Queue()
    coro = _run_text_streaming(demo_server, text, queue)
    return StreamingResponse(_make_sse_stream(coro, queue, demo_server.file_store), media_type="text/event-stream")


def stream_file_message(
    demo_server: "DemoServer",
    data: bytes,
    *,
    caption: str = "",
    force_document: bool = False,
    voice_note: bool = False,
    video_note: bool = False,
) -> StreamingResponse:
    """Send a file message and return an SSE ``StreamingResponse``."""
    queue: asyncio.Queue[ServerlessMessage | object] = asyncio.Queue()
    coro = _run_file_streaming(
        demo_server,
        data,
        queue,
        caption=caption,
        force_document=force_document,
        voice_note=voice_note,
        video_note=video_note,
    )
    return StreamingResponse(_make_sse_stream(coro, queue, demo_server.file_store), media_type="text/event-stream")
