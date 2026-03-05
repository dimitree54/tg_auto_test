"""Drain all bot responses from a conversation and serialize them."""

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
