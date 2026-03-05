"""Telethon-oriented fallback SSE streams for demo actions."""

from collections.abc import AsyncIterator

from fastapi.responses import StreamingResponse
from telethon.tl.functions.messages import SendVoteRequest
from telethon.tl.functions.payments import SendStarsFormRequest
from telethon.tl.types import InputInvoiceMessage

from tg_auto_test.demo_ui.server.response_drain import drain_sse_events
from tg_auto_test.demo_ui.server.serialize import serialize_message
from tg_auto_test.demo_ui.server.trace_stream import (
    build_trace_event,
    serialize_done_event,
    serialize_message_event,
    serialize_trace_event,
)


def _mode_marker(trace_id: str, action_name: str) -> str:
    marker = build_trace_event(
        trace_id,
        scope="server",
        name="mode_selected",
        payload={"action": action_name, "mode": "telethon_fallback"},
    )
    return serialize_trace_event(marker)


def stream_text_fallback(demo_server: object, text: str, trace_id: str) -> StreamingResponse:
    """Fallback for text requests via public conversation API."""

    async def _stream() -> AsyncIterator[str]:
        yield _mode_marker(trace_id, "send_text")
        async with demo_server.client.conversation(demo_server.peer, timeout=demo_server.timeout) as conv:
            await conv.send_message(text)
            async for chunk in drain_sse_events(conv, demo_server.file_store):
                yield chunk

    return StreamingResponse(_stream(), media_type="text/event-stream")


def stream_file_fallback(  # noqa: PLR0913
    demo_server: object,
    data: bytes,
    trace_id: str,
    *,
    caption: str = "",
    force_document: bool = False,
    voice_note: bool = False,
    video_note: bool = False,
) -> StreamingResponse:
    """Fallback for file requests via public conversation API."""

    async def _stream() -> AsyncIterator[str]:
        yield _mode_marker(trace_id, "send_file")
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

    return StreamingResponse(_stream(), media_type="text/event-stream")


def stream_payment_fallback(demo_server: object, message_id: int, trace_id: str) -> StreamingResponse:
    """Fallback for invoice payment via TL request."""

    async def _stream() -> AsyncIterator[str]:
        yield _mode_marker(trace_id, "pay_stars")
        peer = await demo_server.client.get_input_entity(demo_server.peer)
        tl_request = SendStarsFormRequest(
            form_id=message_id,
            invoice=InputInvoiceMessage(peer=peer, msg_id=message_id),
        )
        async with demo_server.client.conversation(demo_server.peer, timeout=demo_server.timeout) as conv:
            await demo_server.client(tl_request)
            async for chunk in drain_sse_events(conv, demo_server.file_store):
                yield chunk

    return StreamingResponse(_stream(), media_type="text/event-stream")


def stream_callback_fallback(demo_server: object, message_id: int, data: str, trace_id: str) -> StreamingResponse:
    """Fallback for callback button clicks via message.click."""

    async def _stream() -> AsyncIterator[str]:
        yield _mode_marker(trace_id, "callback")
        msg = await demo_server.client.get_messages(demo_server.peer, ids=message_id)
        response = await msg.click(data=data.encode())
        yield serialize_message_event(await serialize_message(response, demo_server.file_store))
        yield serialize_done_event()

    return StreamingResponse(_stream(), media_type="text/event-stream")


def stream_poll_fallback(
    demo_server: object, message_id: int, option_ids: list[int], trace_id: str
) -> StreamingResponse:
    """Fallback for poll voting via TL request."""

    async def _stream() -> AsyncIterator[str]:
        yield _mode_marker(trace_id, "poll_vote")
        peer = await demo_server.client.get_input_entity(demo_server.peer)
        vote_request = SendVoteRequest(peer=peer, msg_id=message_id, options=[bytes([i]) for i in option_ids])
        async with demo_server.client.conversation(demo_server.peer, timeout=demo_server.timeout) as conv:
            await demo_server.client(vote_request)
            async for chunk in drain_sse_events(conv, demo_server.file_store):
                yield chunk

    return StreamingResponse(_stream(), media_type="text/event-stream")
