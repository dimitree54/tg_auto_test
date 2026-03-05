"""Run a handler concurrently while streaming responses via an asyncio.Queue."""

import asyncio
from collections import deque
from collections.abc import Awaitable, Callable

from telethon.tl.types import LabeledPrice

from tg_auto_test.test_utils.models import FileData, ServerlessMessage, TelegramApiCall
from tg_auto_test.test_utils.poll_vote_handler import PollTracker
from tg_auto_test.test_utils.response_processor import _MESSAGE_METHODS, process_api_call

_SENTINEL = object()


def _build_hook(
    queue: "asyncio.Queue[ServerlessMessage | object]",
    file_store: dict[str, FileData],
    invoices: dict[int, dict[str, str | int | list[LabeledPrice]]],
    click_callback: Callable[[int, str], Awaitable[ServerlessMessage]],
    outbox: deque[ServerlessMessage],
    poll_tracker: PollTracker | None,
) -> Callable[[TelegramApiCall], None]:
    """Return a callback that converts each API call to a message and enqueues it."""

    def _on_api_call(call: TelegramApiCall) -> None:
        if call.api_method not in _MESSAGE_METHODS:
            return
        message = process_api_call(call, file_store, invoices, click_callback, poll_tracker)
        if message._is_edit:  # noqa: SLF001
            _replace_edited_in_outbox(outbox, message)
        else:
            outbox.append(message)
        queue.put_nowait(message)

    return _on_api_call


def _replace_edited_in_outbox(outbox: deque[ServerlessMessage], edited: ServerlessMessage) -> None:
    for i, existing in enumerate(outbox):
        if existing.id == edited.id:
            outbox[i] = edited
            return
    outbox.append(edited)


async def run_handler_streaming(
    client: object,
    payload: object,
    queue: "asyncio.Queue[ServerlessMessage | object]",
) -> None:
    """Run the PTB handler as a background task, streaming responses into *queue*.

    Installs an ``on_api_call`` hook on the client's stub request so that
    each bot response is enqueued the instant the handler produces it.
    A sentinel is placed on the queue when the handler finishes.
    """
    request = client._request  # noqa: SLF001
    previous_hook = request.on_api_call
    hook = _build_hook(
        queue,
        request.file_store,
        client._invoices,  # noqa: SLF001
        client._handle_click,  # noqa: SLF001
        client._outbox,  # noqa: SLF001
        client._poll_tracker,  # noqa: SLF001
    )
    request.on_api_call = hook
    try:
        update_processor = client._update_processor  # noqa: SLF001
        await update_processor.process_update(client, payload)
    finally:
        request.on_api_call = previous_hook
        queue.put_nowait(_SENTINEL)
