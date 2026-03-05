"""Reproduce GitHub issue #22: Demo server drops subsequent bot messages.

When a bot handler sends multiple messages (e.g. two reply_text calls),
the demo server route handlers call ``conv.get_response()`` only once.
This means only the first bot message is returned to the frontend;
all subsequent messages remain in the outbox and are silently lost.

This test creates a mock conversation that queues multiple responses
and verifies that the demo server endpoint returns ALL of them, not
just the first one.
"""

from collections import deque
import io
from typing import cast
from unittest.mock import AsyncMock, MagicMock  # noqa: TID251

from fastapi.testclient import TestClient

from tg_auto_test.demo_ui.server.demo_server import DemoClientProtocol, DemoServer
from tg_auto_test.test_utils.models import ServerlessMessage


class MultiResponseConversation:
    """Mock conversation that queues multiple bot responses."""

    def __init__(self, responses: list[ServerlessMessage]) -> None:
        self._responses: deque[ServerlessMessage] = deque(responses)
        self.send_message = AsyncMock()
        self.send_file = AsyncMock()

    async def get_response(self) -> ServerlessMessage:
        if not self._responses:
            raise RuntimeError("No pending response.")
        return self._responses.popleft()

    async def __aenter__(self) -> "MultiResponseConversation":
        return self

    async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        return None

    @property
    def pending_count(self) -> int:
        return len(self._responses)


def _make_multi_response_client(
    responses: list[ServerlessMessage],
) -> tuple[MagicMock, MultiResponseConversation]:
    """Build a mock client whose conversation yields multiple responses."""
    conv = MultiResponseConversation(responses)

    mock_client = MagicMock()
    mock_client.connect = AsyncMock()
    mock_client.disconnect = AsyncMock()
    mock_client.conversation.return_value = conv
    return mock_client, conv


def test_message_endpoint_returns_all_bot_responses() -> None:
    """POST /api/message must return ALL bot responses, not just the first.

    The bot sends two text messages. The endpoint should return both.
    Currently it only calls get_response() once, so the second message
    is silently dropped.
    """
    first = ServerlessMessage(id=1, text="First response")
    second = ServerlessMessage(id=2, text="Second response")

    mock_client, conv = _make_multi_response_client([first, second])

    server = DemoServer(cast(DemoClientProtocol, mock_client), "test_bot")
    app = server.create_app()

    with TestClient(app) as client:
        response = client.post("/api/message", json={"text": "/start"})

    assert response.status_code == 200

    # The endpoint currently returns a single MessageResponse.
    # At minimum, all responses must be consumed from the conversation.
    # The second message should NOT be left stranded in the outbox.
    assert conv.pending_count == 0, (
        f"Expected all responses consumed, but {conv.pending_count} "
        f"message(s) still pending in outbox. "
        f"Bug: get_response() called only once, 'Second response' dropped."
    )


def test_photo_endpoint_returns_all_bot_responses() -> None:
    """POST /api/photo must return ALL bot responses, not just the first.

    Same as above but exercises the upload_handlers.py code path.
    """
    first = ServerlessMessage(id=10, text="Got your photo!")
    second = ServerlessMessage(id=11, text="Processing complete.")

    mock_client, conv = _make_multi_response_client([first, second])

    server = DemoServer(cast(DemoClientProtocol, mock_client), "test_bot")
    app = server.create_app()

    image_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    with TestClient(app) as client:
        response = client.post(
            "/api/photo",
            files={"file": ("img.png", io.BytesIO(image_bytes), "image/png")},
        )

    assert response.status_code == 200

    assert conv.pending_count == 0, (
        f"Expected all responses consumed, but {conv.pending_count} "
        f"message(s) still pending in outbox. "
        f"Bug: upload handler calls get_response() only once."
    )


def test_document_endpoint_returns_all_bot_responses() -> None:
    """POST /api/document must return ALL bot responses, not just the first."""
    first = ServerlessMessage(id=20, text="Got your document!")
    second = ServerlessMessage(id=21, text="Document processed.")

    mock_client, conv = _make_multi_response_client([first, second])

    server = DemoServer(cast(DemoClientProtocol, mock_client), "test_bot")
    app = server.create_app()

    with TestClient(app) as client:
        response = client.post(
            "/api/document",
            files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
        )

    assert response.status_code == 200

    assert conv.pending_count == 0, (
        f"Expected all responses consumed, but {conv.pending_count} "
        f"message(s) still pending in outbox. "
        f"Bug: upload handler calls get_response() only once."
    )
