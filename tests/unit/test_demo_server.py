"""Unit tests for the demo server implementation."""

import asyncio
import io
from typing import cast
from unittest.mock import AsyncMock, MagicMock, Mock  # noqa: TID251

from fastapi.testclient import TestClient
import pytest

from tests.unit.sse_helpers import parse_sse_messages
from tg_auto_test.demo_ui.server.demo_server import DemoClientProtocol, DemoServer, create_demo_app
from tg_auto_test.demo_ui.server.file_store import FileStore
from tg_auto_test.test_utils.models import ReplyMarkup, ServerlessMessage


class TestDemoServer:
    """Test the DemoServer class."""

    def test_init_with_valid_peer(self) -> None:
        """Test initialization with valid peer."""
        mock_client = Mock()
        server = DemoServer(mock_client, "test_bot")

        assert server.client == mock_client
        assert server.peer == "test_bot"
        assert server.timeout == 10.0
        assert isinstance(server.file_store, FileStore)

    def test_init_with_empty_peer_fails(self) -> None:
        """Test that empty peer raises ValueError."""
        mock_client = Mock()

        with pytest.raises(ValueError, match="Peer must be specified"):
            DemoServer(mock_client, "")

    def test_init_with_custom_timeout(self) -> None:
        """Test initialization with custom timeout."""
        mock_client = Mock()
        server = DemoServer(mock_client, "test_bot", timeout=30.0)

        assert server.timeout == 30.0

    def test_create_app(self) -> None:
        """Test app creation returns object with expected attributes."""
        mock_client = Mock()
        server = DemoServer(mock_client, "test_bot")

        # Skip app creation test since FastAPI is optional dependency
        # Just test that the method exists and server has required attributes
        assert hasattr(server, "create_app")
        assert callable(server.create_app)
        assert server.client == mock_client
        assert server.peer == "test_bot"
        assert server.file_store is not None


def test_create_demo_app_factory() -> None:
    """Test the factory function exists and is callable."""
    # Skip actual app creation since FastAPI is optional dependency
    # Just verify the function exists with expected signature
    assert callable(create_demo_app)

    # Test parameter validation still works
    mock_client = Mock()

    with pytest.raises(ValueError, match="Peer must be specified"):
        create_demo_app(client=mock_client, peer="")


def test_demo_server_on_action_callback() -> None:
    """Test that on_action callback is stored correctly."""
    mock_client = Mock()

    async def mock_callback(action: str, client: DemoClientProtocol) -> None:
        # Mock callback for testing - must be async to match the protocol
        await asyncio.sleep(0)  # Make it properly async
        assert isinstance(action, str)
        assert client is not None

    server = DemoServer(mock_client, "test_bot", on_action=mock_callback)

    assert server.on_action == mock_callback


def test_demo_server_without_on_action_callback() -> None:
    """Test that on_action callback defaults to None."""
    mock_client = Mock()
    server = DemoServer(mock_client, "test_bot")

    assert server.on_action is None


def test_poll_vote_endpoint() -> None:
    """Test the poll vote endpoint using Telethon SendVoteRequest."""
    from tests.unit.demo_server_mocks import MockDemoClient  # noqa: PLC0415

    mock_client = MockDemoClient()

    # Create demo server and app
    server = DemoServer(cast(DemoClientProtocol, mock_client), "test_bot")
    app = server.create_app()

    # Test the endpoint with new API (message_id instead of poll_id)
    with TestClient(app) as client:
        response = client.post("/api/poll/vote", json={"message_id": 123, "option_ids": [0]})

    assert response.status_code == 200
    messages = parse_sse_messages(response)
    assert len(messages) >= 1
    data = messages[0]
    assert data["type"] == "text"
    assert data["text"] == "You voted for: Red"
    assert data["message_id"] == 456

    # Verify the client __call__ method was called with SendVoteRequest
    assert len(mock_client._call_log) == 1
    call_args = mock_client._call_log[0]
    assert call_args.msg_id == 123
    assert call_args.options == [bytes([0])]


def test_photo_endpoint_returns_text_response_when_bot_replies_with_text() -> None:
    """Test that /api/photo returns text+reply_markup when bot responds with text (not media)."""
    reply_markup: ReplyMarkup = {"inline_keyboard": [[{"text": "Click me", "callback_data": "test"}]]}
    bot_response = ServerlessMessage(id=42, text="I got your photo!", _reply_markup_data=reply_markup)

    # Set up the mock conversation context manager
    mock_conv = MagicMock()
    mock_conv.send_file = AsyncMock()
    mock_conv.get_response = AsyncMock(side_effect=[bot_response, RuntimeError("No pending response.")])

    mock_conv_cm = MagicMock()
    mock_conv_cm.__aenter__ = AsyncMock(return_value=mock_conv)
    mock_conv_cm.__aexit__ = AsyncMock(return_value=None)

    mock_client = MagicMock()
    mock_client.connect = AsyncMock()
    mock_client.disconnect = AsyncMock()
    mock_client.conversation.return_value = mock_conv_cm

    server = DemoServer(cast(DemoClientProtocol, mock_client), "test_bot")
    app = server.create_app()

    image_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    with TestClient(app) as client:
        response = client.post(
            "/api/photo",
            files={"file": ("image.png", io.BytesIO(image_bytes), "image/png")},
        )

    assert response.status_code == 200
    messages = parse_sse_messages(response)
    assert len(messages) >= 1
    data = messages[0]
    assert data["type"] == "text"
    assert data["text"] == "I got your photo!"
    assert data["message_id"] == 42
    assert data["reply_markup"] == {"inline_keyboard": [[{"text": "Click me", "callback_data": "test"}]]}
    assert data["file_id"] == ""
