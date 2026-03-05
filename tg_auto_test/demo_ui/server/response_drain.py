"""Drain all bot responses from a conversation and serialize them."""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING  # noqa: TID251

from tg_auto_test.demo_ui.server.api_models import MessageResponse
from tg_auto_test.demo_ui.server.file_store import FileStore
from tg_auto_test.demo_ui.server.serialize import serialize_message

if TYPE_CHECKING:
    from tg_auto_test.demo_ui.server.demo_server import DemoConversationProtocol


async def drain_and_serialize(
    conv: "DemoConversationProtocol",
    file_store: FileStore,
) -> list[MessageResponse]:
    """Get all pending bot responses from the conversation and serialize them.

    Calls get_response() repeatedly until the outbox is empty.
    """
    responses: list[MessageResponse] = []
    first = await conv.get_response()
    responses.append(await serialize_message(first, file_store))
    while True:
        try:
            msg = await conv.get_response()
        except RuntimeError:
            break
        responses.append(await serialize_message(msg, file_store))
    return responses


async def drain_sse_events(
    conv: "DemoConversationProtocol",
    file_store: FileStore,
) -> AsyncIterator[str]:
    """Yield SSE-formatted events as bot responses arrive.

    Each event is ``data: <json>\\n\\n``. A final ``data: [DONE]\\n\\n``
    signals the stream end.
    """
    first = await conv.get_response()
    serialized = await serialize_message(first, file_store)
    yield f"data: {serialized.model_dump_json()}\n\n"
    while True:
        try:
            msg = await conv.get_response()
        except RuntimeError:
            break
        serialized = await serialize_message(msg, file_store)
        yield f"data: {serialized.model_dump_json()}\n\n"
    yield "data: [DONE]\n\n"
