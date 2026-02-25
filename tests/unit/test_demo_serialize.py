"""Unit tests for demo server message serialization."""

from typing import cast
from unittest.mock import Mock  # noqa: TID251

import pytest

from tg_auto_test.demo_ui.server.file_store import FileStore
from tg_auto_test.demo_ui.server.serialize import serialize_message, store_response_file
from tg_auto_test.test_utils.models import ReplyMarkup, ServerlessMessage


@pytest.mark.asyncio
async def test_serialize_text_message() -> None:
    """Test serializing a simple text message."""
    file_store = FileStore()
    message = ServerlessMessage(id=123, text="Hello world")

    result = await serialize_message(message, file_store)

    assert result.type == "text"
    assert result.text == "Hello world"
    assert result.message_id == 123
    assert result.file_id == ""
    assert result.filename == ""
    assert result.entities == []


@pytest.mark.asyncio
async def test_serialize_invoice_message() -> None:
    """Test serializing an invoice message."""
    file_store = FileStore()

    # Create mock invoice
    mock_invoice = Mock()
    mock_invoice.title = "Test Invoice"
    mock_invoice.description = "Test Description"
    mock_invoice.currency = "USD"
    mock_invoice.total_amount = 1000

    message = ServerlessMessage(id=456, _invoice_data=mock_invoice)

    result = await serialize_message(message, file_store)

    assert result.type == "invoice"
    assert result.message_id == 456
    assert result.title == "Test Invoice"
    assert result.description == "Test Description"
    assert result.currency == "USD"
    assert result.total_amount == 1000


@pytest.mark.asyncio
async def test_serialize_message_with_reply_markup() -> None:
    """Test serializing message with reply markup."""
    file_store = FileStore()

    # Create reply markup with buttons
    reply_markup = cast(
        ReplyMarkup,
        {
            "inline_keyboard": [
                [{"text": "Button 1", "callback_data": "data1"}],
                [{"text": "Button 2", "callback_data": "data2"}],
            ]
        },
    )

    message = ServerlessMessage(id=111, text="Choose option", _reply_markup_data=reply_markup)

    result = await serialize_message(message, file_store)

    assert result.type == "text"
    assert result.text == "Choose option"
    # Check that reply_markup was converted from .buttons property
    assert result.reply_markup is not None
    assert result.reply_markup["inline_keyboard"] is not None


@pytest.mark.asyncio
async def test_serialize_document_message() -> None:
    """Test serializing a document message without media."""
    file_store = FileStore()

    # Create mock document without voice/video attributes
    mock_document = Mock()
    mock_document.attributes = []

    message = ServerlessMessage(id=999, _media_document=mock_document)

    result = await serialize_message(message, file_store)

    assert result.type == "document"
    assert result.message_id == 999
    # File ID is now a UUID, so just check it's not empty
    assert result.file_id != ""
    assert len(result.file_id) > 10  # UUID format


@pytest.mark.asyncio
async def test_store_response_file_fallback() -> None:
    """Test storing response file using fallback data when no media available."""
    file_store = FileStore()

    # Create a message that will return None for download_media
    message = ServerlessMessage()

    result = await store_response_file(
        "fallback_id", message, file_store, "fallback.txt", "text/plain", b"fallback data"
    )

    assert result == "fallback.txt"
    stored = file_store.get("fallback_id")
    assert stored == ("fallback.txt", "text/plain", b"fallback data")


@pytest.mark.asyncio
async def test_serialize_poll_message() -> None:
    """Test serializing a poll message."""
    file_store = FileStore()

    # Create mock poll data that matches what stub_request_media produces
    poll_data = {
        "id": "poll_123",
        "question": "What is your favorite color?",
        "options": [
            {"text": "Red"},
            {"text": "Blue"},
            {"text": "Green"},
        ],
    }

    message = ServerlessMessage(id=789, _poll_data=poll_data)

    result = await serialize_message(message, file_store)

    assert result.type == "poll"
    assert result.message_id == 789
    assert result.poll_question == "What is your favorite color?"
    # Poll ID is hashed in real Telethon, so just check it's non-empty string
    assert result.poll_id != ""
    assert isinstance(result.poll_id, str)
    # Verify poll_options is non-empty and contains the correct options
    assert result.poll_options is not None
    assert len(result.poll_options) == 3
    assert result.poll_options[0]["text"] == "Red"
    assert result.poll_options[0]["voter_count"] == 0
    assert result.poll_options[1]["text"] == "Blue"
    assert result.poll_options[1]["voter_count"] == 0
    assert result.poll_options[2]["text"] == "Green"
    assert result.poll_options[2]["voter_count"] == 0
