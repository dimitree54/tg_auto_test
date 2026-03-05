"""Drain all bot responses from a conversation and serialize them."""

import asyncio
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING  # noqa: TID251

from tg_auto_test.demo_ui.server.api_models import MessageResponse
from tg_auto_test.demo_ui.server.file_store import FileStore
from tg_auto_test.demo_ui.server.serialize import serialize_message
from tg_auto_test.test_utils.models import ServerlessMessage
from tg_auto_test.test_utils.streaming_processor import _SENTINEL

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
    """Yield SSE events from a conversation whose outbox is already populated.

    Use ``stream_sse_from_queue`` for the concurrent-handler path.
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


async def stream_sse_from_queue(
    queue: "asyncio.Queue[ServerlessMessage | object]",
    file_store: FileStore,
) -> AsyncIterator[str]:
    """Yield SSE events by reading from an ``asyncio.Queue`` fed by the handler.

    The handler runs concurrently and puts ``ServerlessMessage`` objects on the
    queue as they are produced. A sentinel signals the handler is done.
    """
    while True:
        item = await queue.get()
        if item is _SENTINEL:
            break
        serialized = await serialize_message(item, file_store)  # type: ignore[arg-type]
        yield f"data: {serialized.model_dump_json()}\n\n"
    yield "data: [DONE]\n\n"
