"""Unit tests for the demo server implementation."""

import asyncio
import io
from typing import cast
from unittest.mock import Mock  # noqa: TID251

from fastapi.testclient import TestClient
import pytest
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters

from tests.unit.sse_helpers import make_png_bytes, parse_sse_events, parse_sse_messages
from tg_auto_test.demo_ui.server.demo_server import DemoClientProtocol, DemoServer, create_demo_app
from tg_auto_test.demo_ui.server.file_store import FileStore
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


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

        assert hasattr(server, "create_app")
        assert callable(server.create_app)
        assert server.client == mock_client
        assert server.peer == "test_bot"
        assert server.file_store is not None


def test_create_demo_app_factory() -> None:
    """Test the factory function exists and is callable."""
    assert callable(create_demo_app)

    mock_client = Mock()

    with pytest.raises(ValueError, match="Peer must be specified"):
        create_demo_app(client=mock_client, peer="")


def test_demo_server_on_action_callback() -> None:
    """Test that on_action callback is stored correctly."""
    mock_client = Mock()

    async def mock_callback(action: str, client: DemoClientProtocol) -> None:
        await asyncio.sleep(0)
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

    server = DemoServer(cast(DemoClientProtocol, mock_client), "test_bot")
    app = server.create_app()

    with TestClient(app) as client:
        response = client.post("/api/poll/vote", json={"message_id": 123, "option_ids": [0]})

    assert response.status_code == 200
    messages = parse_sse_messages(response)
    assert len(messages) >= 1
    data = messages[0]
    assert data["type"] == "text"
    assert data["text"] == "You voted for: Red"
    assert data["message_id"] == 456

    assert len(mock_client._call_log) == 1
    call_args = mock_client._call_log[0]
    assert call_args.msg_id == 123
    assert call_args.options == [bytes([0])]


def test_message_endpoint_uses_telethon_fallback_when_serverless_attrs_missing() -> None:
    """Text requests should work via conversation.send_message fallback."""
    from tests.unit.demo_server_mocks import MockDemoClient  # noqa: PLC0415

    mock_client = MockDemoClient()
    server = DemoServer(cast(DemoClientProtocol, mock_client), "test_bot")
    app = server.create_app()

    with TestClient(app) as client:
        response = client.post("/api/message", json={"text": "hello"})

    assert response.status_code == 200
    events = parse_sse_events(response)
    trace_events = [event["data"] for event in events if event["event"] == "trace"]
    assert any(
        event["name"] == "mode_selected" and event["payload"]["mode"] == "telethon_fallback" for event in trace_events
    )
    messages = [event["data"] for event in events if event["event"] == "message"]
    assert len(messages) == 1
    assert messages[0]["text"] == "You voted for: Red"
    assert mock_client._sent_messages == ["hello"]


def test_document_endpoint_uses_telethon_fallback_when_serverless_attrs_missing() -> None:
    """File requests should work via conversation.send_file fallback."""
    from tests.unit.demo_server_mocks import MockDemoClient  # noqa: PLC0415

    mock_client = MockDemoClient()
    server = DemoServer(cast(DemoClientProtocol, mock_client), "test_bot")
    app = server.create_app()

    with TestClient(app) as client:
        response = client.post("/api/document", files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")})

    assert response.status_code == 200
    messages = parse_sse_messages(response)
    assert len(messages) == 1
    assert messages[0]["text"] == "You voted for: Red"
    assert len(mock_client._sent_files) == 1
    assert mock_client._sent_files[0]["force_document"] is True


async def _photo_text_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler that replies to any photo with text + inline keyboard."""
    del context
    if not update.message:
        return
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Click me", callback_data="test")]])
    await update.message.reply_text("I got your photo!", reply_markup=keyboard)


def _build_photo_text_reply_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(MessageHandler(filters.PHOTO, _photo_text_reply_handler))
    return app


def test_photo_endpoint_returns_text_response_when_bot_replies_with_text() -> None:
    """Test that /api/photo returns text+reply_markup when bot responds with text."""
    real_client = ServerlessTelegramClient(_build_photo_text_reply_app)

    server = DemoServer(cast(DemoClientProtocol, real_client), "test_bot")
    app = server.create_app()

    with TestClient(app) as client:
        response = client.post(
            "/api/photo",
            files={"file": ("image.png", io.BytesIO(make_png_bytes()), "image/png")},
        )

    assert response.status_code == 200
    messages = parse_sse_messages(response)
    assert len(messages) >= 1
    data = messages[0]
    assert data["type"] == "text"
    assert data["text"] == "I got your photo!"
    markup = data["reply_markup"]
    assert "inline_keyboard" in markup
    keyboard = markup["inline_keyboard"]
    assert keyboard[0][0]["text"] == "Click me"
    assert keyboard[0][0]["callback_data"] == "test"
    assert data["file_id"] == ""
