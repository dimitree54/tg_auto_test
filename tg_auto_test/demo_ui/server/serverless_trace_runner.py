"""Serverless-only trace runner for demo UI streaming endpoints."""

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import suppress

from fastapi.responses import StreamingResponse
from telegram.ext import CallbackContext

from tg_auto_test.demo_ui.server.serialize import serialize_message
from tg_auto_test.demo_ui.server.serverless_trace_hooks import TraceState, install_request_hook
from tg_auto_test.demo_ui.server.trace_stream import (
    serialize_done_event,
    serialize_message_event,
    serialize_trace_event,
)
from tg_auto_test.test_utils.exceptions import BotNoResponseError
from tg_auto_test.test_utils.models import ServerlessMessage

_SENTINEL = object()


async def _run_stream(
    demo_server: object,
    trace_id: str,
    action_name: str,
    request_payload: dict[str, object],
    queue: "asyncio.Queue[object]",
    run_action: Callable[[], Awaitable[None]],
    on_action_name: str | None,
) -> None:
    client = demo_server.client
    state = TraceState(trace_id, queue)
    app = client._application  # noqa: SLF001
    previous_hook = install_request_hook(client, state)

    async def _error_handler(_update: object, context: CallbackContext) -> None:
        await asyncio.sleep(0)
        if context.error is not None:
            state.emit_exception(context.error, "ptb_error_handler")

    app.add_error_handler(_error_handler)
    state.emit_trace("server", "request_started", {"action": action_name})
    state.emit_trace("server", "update_prepared", {"action": action_name, "request": request_payload})
    try:
        await run_action()
        if state.message_count == 0:
            raise BotNoResponseError("Bot did not respond to the action.")
        if on_action_name is not None and demo_server.on_action is not None:
            await demo_server.on_action(on_action_name, client)
        state.emit_trace("server", "request_completed", {"action": action_name, "message_count": state.message_count})
    except Exception as error:
        state.emit_exception(error, "demo_runner")
        state.fail(str(error))
    finally:
        client._request.on_api_call = previous_hook  # noqa: SLF001
        with suppress(ValueError):
            app.remove_error_handler(_error_handler)
        queue.put_nowait(_SENTINEL)


async def _stream_sse(demo_server: object, queue: "asyncio.Queue[object]") -> AsyncIterator[str]:
    while True:
        item = await queue.get()
        if item is _SENTINEL:
            break
        if isinstance(item, ServerlessMessage):
            serialized = await serialize_message(item, demo_server.file_store)
            yield serialize_message_event(serialized)
            continue
        yield serialize_trace_event(item)
    yield serialize_done_event()


def stream_serverless_action(
    demo_server: object,
    *,
    action_name: str,
    request_payload: dict[str, object],
    trace_id: str,
    run_action: Callable[[], Awaitable[None]],
    on_action_name: str | None = None,
) -> StreamingResponse:
    """Stream a serverless demo action as typed SSE events."""
    queue: asyncio.Queue[object] = asyncio.Queue()

    async def _stream() -> AsyncIterator[str]:
        task = asyncio.create_task(
            _run_stream(demo_server, trace_id, action_name, request_payload, queue, run_action, on_action_name)
        )
        try:
            async for chunk in _stream_sse(demo_server, queue):
                yield chunk
        finally:
            await task

    return StreamingResponse(_stream(), media_type="text/event-stream")
