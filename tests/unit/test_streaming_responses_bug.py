"""Reproduce GitHub issue #23: Demo UI does not show intermediate bot messages.

The POST /api/message endpoint used to batch all responses into a single
JSON array, meaning intermediate bot messages were invisible until the
handler completed.

The fix uses SSE (Server-Sent Events) via ``StreamingResponse`` so each
response is flushed to the client as soon as ``get_response()`` resolves.
"""

import asyncio
from collections import deque
import json
import time
from typing import cast
from unittest.mock import AsyncMock, MagicMock  # noqa: TID251

from fastapi.testclient import TestClient
import pytest

from tests.unit.sse_helpers import parse_sse_messages
from tg_auto_test.demo_ui.server.demo_server import DemoClientProtocol, DemoServer
from tg_auto_test.demo_ui.server.file_store import FileStore
from tg_auto_test.demo_ui.server.response_drain import drain_sse_events
from tg_auto_test.test_utils.models import ServerlessMessage

_HANDLER_DELAY = 0.3


class SlowHandlerConversation:
    """Mock conversation where the second get_response() is delayed."""

    def __init__(self, messages: list[ServerlessMessage], delay: float) -> None:
        self._messages: deque[ServerlessMessage] = deque(messages)
        self._delay = delay
        self._first_returned = False
        self.send_message = AsyncMock()

    async def get_response(self) -> ServerlessMessage:
        if not self._messages:
            raise RuntimeError("No pending response.")
        if self._first_returned:
            await asyncio.sleep(self._delay)
        self._first_returned = True
        return self._messages.popleft()

    async def __aenter__(self) -> "SlowHandlerConversation":
        return self

    async def __aexit__(self, *args: object) -> None:
        return None


def _make_slow_handler_app(
    messages: list[ServerlessMessage],
    delay: float = _HANDLER_DELAY,
) -> DemoServer:
    conv = SlowHandlerConversation(messages, delay)
    mock_client = MagicMock()
    mock_client.connect = AsyncMock()
    mock_client.disconnect = AsyncMock()
    mock_client.conversation.return_value = conv
    return DemoServer(cast(DemoClientProtocol, mock_client), "test_bot")


def test_message_endpoint_uses_sse_content_type() -> None:
    """POST /api/message must return content-type text/event-stream."""
    server = _make_slow_handler_app([ServerlessMessage(id=1, text="hi")], delay=0)
    app = server.create_app()

    with TestClient(app) as client:
        resp = client.post("/api/message", json={"text": "hello"})

    assert resp.status_code == 200
    content_type = resp.headers.get("content-type", "")
    assert "text/event-stream" in content_type


def test_sse_events_contain_all_messages() -> None:
    """The SSE stream must contain every bot response plus a [DONE] sentinel."""
    server = _make_slow_handler_app(
        [ServerlessMessage(id=1, text="first"), ServerlessMessage(id=2, text="second")],
        delay=0,
    )
    app = server.create_app()

    with TestClient(app) as client:
        resp = client.post("/api/message", json={"text": "/go"})

    messages = parse_sse_messages(resp)
    assert len(messages) == 2
    assert messages[0]["text"] == "first"
    assert messages[1]["text"] == "second"
    assert "data: [DONE]" in resp.text


@pytest.mark.asyncio
async def test_drain_sse_events_yields_incrementally() -> None:
    """drain_sse_events must yield the first event before the second resolves.

    This proves the async generator yields each SSE chunk as soon as the
    underlying get_response() returns, rather than collecting everything
    into a batch.
    """
    conv = SlowHandlerConversation(
        [ServerlessMessage(id=1, text="Processing..."), ServerlessMessage(id=2, text="Done!")],
        delay=_HANDLER_DELAY,
    )
    file_store = FileStore()

    timestamps: list[float] = []
    events: list[str] = []
    start = time.monotonic()

    async for chunk in drain_sse_events(conv, file_store):
        timestamps.append(time.monotonic() - start)
        events.append(chunk)

    # 3 chunks: first message, second message, [DONE]
    assert len(events) == 3

    first_data = json.loads(events[0].removeprefix("data: ").strip())
    assert first_data["text"] == "Processing..."

    second_data = json.loads(events[1].removeprefix("data: ").strip())
    assert second_data["text"] == "Done!"

    assert events[2].strip() == "data: [DONE]"

    # First event should arrive near-instantly (before the delay)
    assert timestamps[0] < _HANDLER_DELAY * 0.5, f"First SSE event at {timestamps[0]:.3f}s — should be near-instant."
    # Second event should arrive after the delay
    assert timestamps[1] >= _HANDLER_DELAY * 0.8, (
        f"Second SSE event at {timestamps[1]:.3f}s — should reflect the delay."
    )
