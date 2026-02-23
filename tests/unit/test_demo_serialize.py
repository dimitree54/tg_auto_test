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

    message = ServerlessMessage(id=456, invoice_data=mock_invoice)

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

    # Use simpler reply markup structure
    reply_markup = cast(ReplyMarkup, {"type": "inline_keyboard"})

    message = ServerlessMessage(id=111, text="Choose option", reply_markup_data=reply_markup)

    result = await serialize_message(message, file_store)

    assert result.type == "text"
    assert result.text == "Choose option"
    assert result.reply_markup == reply_markup


@pytest.mark.asyncio
async def test_serialize_document_message() -> None:
    """Test serializing a document message without media."""
    file_store = FileStore()

    # Create mock document without voice/video attributes
    mock_document = Mock()
    mock_document.attributes = []

    message = ServerlessMessage(id=999, media_document=mock_document, response_file_id="doc_456")

    result = await serialize_message(message, file_store)

    assert result.type == "document"
    assert result.message_id == 999
    assert result.file_id == "doc_456"


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
