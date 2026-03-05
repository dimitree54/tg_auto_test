"""Reproduce GitHub issue #23 (reopened): SSE events not delivered incrementally.

The original fix used ``drain_sse_events`` after ``conv.send_message()``, but
``send_message`` awaits the entire PTB handler.  All messages were already
queued before draining started, so SSE events arrived at the same instant.

The fix uses ``run_handler_streaming`` which installs an ``on_api_call`` hook
that enqueues each response the instant the handler produces it.  A background
task runs the handler while ``stream_sse_from_queue`` yields SSE events
concurrently.
"""

import asyncio
import time

import pytest
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from tg_auto_test.demo_ui.server.file_store import FileStore
from tg_auto_test.demo_ui.server.response_drain import stream_sse_from_queue
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient
from tg_auto_test.test_utils.streaming_processor import run_handler_streaming

_WORK_SECONDS = 0.3


async def _slow_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.message:
        return
    await update.message.reply_text("Processing...")
    await asyncio.sleep(_WORK_SECONDS)
    await update.message.reply_text("Done!")


def _build_app(builder: ApplicationBuilder) -> ApplicationBuilder:
    app = builder.build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _slow_handler))
    return app


@pytest.mark.asyncio
async def test_sse_events_arrive_incrementally_with_real_handler() -> None:
    """SSE events must stream as the handler produces them.

    Expected:  event 1 at ~0s, event 2 at ~0.3s  (gap >= work duration)
    """
    client = ServerlessTelegramClient(_build_app)
    await client.connect()

    try:
        client._outbox.clear()
        payload, msg = client._helpers.base_message_update(client._chat_id)
        msg["text"] = "hello"

        queue: asyncio.Queue[object] = asyncio.Queue()
        task = asyncio.create_task(run_handler_streaming(client, payload, queue))

        t0 = time.monotonic()
        event_times: list[float] = []
        event_texts: list[str] = []

        async for chunk in stream_sse_from_queue(queue, FileStore()):
            event_times.append(time.monotonic() - t0)
            event_texts.append(chunk)

        await task

        assert len(event_texts) == 3
        assert "Processing..." in event_texts[0]
        assert "Done!" in event_texts[1]
        assert "[DONE]" in event_texts[2]

        gap = event_times[1] - event_times[0]
        threshold = _WORK_SECONDS * 0.5
        assert gap >= threshold, (
            f"SSE gap {gap:.4f}s < {threshold}s \u2014 both events arrived "
            f"simultaneously because drain starts only after the "
            f"handler finishes (t0={event_times[0]:.4f}s, "
            f"t1={event_times[1]:.4f}s)."
        )
    finally:
        await client.disconnect()
