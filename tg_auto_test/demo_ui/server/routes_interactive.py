"""Interactive route handlers for invoice, poll vote, and callback endpoints."""

from typing import TYPE_CHECKING  # noqa: TID251

from fastapi import HTTPException
from telethon.tl.functions.messages import SendVoteRequest
from telethon.tl.functions.payments import SendStarsFormRequest
from telethon.tl.types import InputInvoiceMessage

from tg_auto_test.demo_ui.server.api_models import (
    CallbackRequest,
    InvoicePayRequest,
    MessageResponse,
    PollVoteRequest,
)
from tg_auto_test.demo_ui.server.serialize import serialize_message

if TYPE_CHECKING:
    from tg_auto_test.demo_ui.server.demo_server import DemoServer


async def handle_pay_invoice(demo_server: "DemoServer", req: InvoicePayRequest) -> MessageResponse:
    """Handle invoice payment request."""
    peer = await demo_server.client.get_input_entity(demo_server.peer)
    request = SendStarsFormRequest(
        form_id=req.message_id,
        invoice=InputInvoiceMessage(peer=peer, msg_id=req.message_id),
    )
    async with demo_server.client.conversation(demo_server.peer, timeout=demo_server.timeout) as conv:
        await demo_server.client(request)
        response = await conv.get_response()
    return await serialize_message(response, demo_server.file_store)


async def handle_callback(demo_server: "DemoServer", req: CallbackRequest) -> MessageResponse:
    """Handle callback query request."""
    msg = await demo_server.client.get_messages(demo_server.peer, ids=req.message_id)
    if not msg:
        raise HTTPException(status_code=404, detail=f"Message {req.message_id} not found")

    click_result = await msg.click(data=req.data.encode())
    # In our implementation, click() always returns ServerlessMessage
    response = click_result
    return await serialize_message(response, demo_server.file_store)


async def handle_poll_vote(demo_server: "DemoServer", request: PollVoteRequest) -> MessageResponse:
    """Handle poll vote by calling Telethon SendVoteRequest."""
    peer = await demo_server.client.get_input_entity(demo_server.peer)

    # Convert option indices to bytes (consistent with model_helpers.py)
    option_bytes = [bytes([i]) for i in request.option_ids]

    # Use Telethon SendVoteRequest pattern
    vote_request = SendVoteRequest(
        peer=peer,
        msg_id=request.message_id,
        options=option_bytes,
    )

    # Execute the request and get response using conversation pattern
    async with demo_server.client.conversation(demo_server.peer, timeout=demo_server.timeout) as conv:
        await demo_server.client(vote_request)
        response = await conv.get_response()

    # Serialize the bot response
    return await serialize_message(response, demo_server.file_store)
