"""Interactive route handlers for invoice, poll vote, and callback endpoints."""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING  # noqa: TID251

from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from telethon.tl.functions.messages import SendVoteRequest
from telethon.tl.functions.payments import SendStarsFormRequest
from telethon.tl.types import InputInvoiceMessage

from tg_auto_test.demo_ui.server.api_models import (
    CallbackRequest,
    InvoicePayRequest,
    MessageResponse,
    PollVoteRequest,
)
from tg_auto_test.demo_ui.server.response_drain import drain_sse_events
from tg_auto_test.demo_ui.server.serialize import serialize_message

if TYPE_CHECKING:
    from tg_auto_test.demo_ui.server.demo_server import DemoServer


def stream_pay_invoice(demo_server: "DemoServer", req: InvoicePayRequest) -> StreamingResponse:
    """Handle invoice payment with SSE streaming responses."""

    async def _stream() -> AsyncIterator[str]:
        peer = await demo_server.client.get_input_entity(demo_server.peer)
        tl_request = SendStarsFormRequest(
            form_id=req.message_id,
            invoice=InputInvoiceMessage(peer=peer, msg_id=req.message_id),
        )
        async with demo_server.client.conversation(demo_server.peer, timeout=demo_server.timeout) as conv:
            await demo_server.client(tl_request)
            async for chunk in drain_sse_events(conv, demo_server.file_store):
                yield chunk
        if demo_server.on_action is not None:
            await demo_server.on_action("pay_stars", demo_server.client)

    return StreamingResponse(_stream(), media_type="text/event-stream")


async def handle_callback(demo_server: "DemoServer", req: CallbackRequest) -> MessageResponse:
    """Handle callback query request."""
    msg = await demo_server.client.get_messages(demo_server.peer, ids=req.message_id)
    if not msg:
        raise HTTPException(status_code=404, detail=f"Message {req.message_id} not found")

    click_result = await msg.click(data=req.data.encode())
    response = click_result
    return await serialize_message(response, demo_server.file_store)


def stream_poll_vote(demo_server: "DemoServer", request: PollVoteRequest) -> StreamingResponse:
    """Handle poll vote with SSE streaming responses."""

    async def _stream() -> AsyncIterator[str]:
        peer = await demo_server.client.get_input_entity(demo_server.peer)
        option_bytes = [bytes([i]) for i in request.option_ids]
        vote_request = SendVoteRequest(
            peer=peer,
            msg_id=request.message_id,
            options=option_bytes,
        )
        async with demo_server.client.conversation(demo_server.peer, timeout=demo_server.timeout) as conv:
            await demo_server.client(vote_request)
            async for chunk in drain_sse_events(conv, demo_server.file_store):
                yield chunk
        if demo_server.on_action is not None:
            await demo_server.on_action("poll_vote", demo_server.client)

    return StreamingResponse(_stream(), media_type="text/event-stream")
