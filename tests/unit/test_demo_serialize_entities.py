"""Unit tests for entity serialization in demo server."""

from unittest.mock import Mock  # noqa: TID251

import pytest
from telethon.tl.types import (
    MessageEntityBold,
    MessageEntityCode,
    MessageEntityItalic,
    MessageEntityMention,
    MessageEntityPre,
    MessageEntitySpoiler,
    MessageEntityStrike,
    MessageEntityTextUrl,
    MessageEntityUnderline,
    MessageEntityUrl,
)

from tg_auto_test.demo_ui.server.file_store import FileStore
from tg_auto_test.demo_ui.server.serialize import serialize_message
from tg_auto_test.demo_ui.server.serialize_entities import serialize_entities, serialize_entity


def _create_mock_message(msg_id: int, text: str, entities: list | None = None) -> Mock:
    """Helper to create mock messages for testing."""
    message = Mock()
    message.id = msg_id
    message.text = text
    message.entities = entities
    message.photo = None
    message.document = None
    message.voice = None
    message.video_note = None
    message.buttons = None
    message.poll = None
    message.invoice = None
    return message


def test_serialize_bold_entity() -> None:
    """Test serializing a bold entity."""
    entity = MessageEntityBold(offset=0, length=4)
    result = serialize_entity(entity)
    expected = {"type": "bold", "offset": 0, "length": 4}
    assert result == expected


def test_serialize_italic_entity() -> None:
    """Test serializing an italic entity."""
    entity = MessageEntityItalic(offset=5, length=3)
    result = serialize_entity(entity)
    expected = {"type": "italic", "offset": 5, "length": 3}
    assert result == expected


def test_serialize_underline_entity() -> None:
    """Test serializing an underline entity."""
    entity = MessageEntityUnderline(offset=2, length=6)
    result = serialize_entity(entity)
    expected = {"type": "underline", "offset": 2, "length": 6}
    assert result == expected


def test_serialize_strikethrough_entity() -> None:
    """Test serializing a strikethrough entity."""
    entity = MessageEntityStrike(offset=1, length=8)
    result = serialize_entity(entity)
    expected = {"type": "strikethrough", "offset": 1, "length": 8}
    assert result == expected


def test_serialize_code_entity() -> None:
    """Test serializing a code entity."""
    entity = MessageEntityCode(offset=10, length=5)
    result = serialize_entity(entity)
    expected = {"type": "code", "offset": 10, "length": 5}
    assert result == expected


def test_serialize_pre_entity_with_language() -> None:
    """Test serializing a pre entity with language."""
    entity = MessageEntityPre(offset=0, length=10, language="python")
    result = serialize_entity(entity)
    expected = {"type": "pre", "offset": 0, "length": 10, "language": "python"}
    assert result == expected


def test_serialize_pre_entity_without_language() -> None:
    """Test serializing a pre entity without language."""
    entity = MessageEntityPre(offset=0, length=10, language="")
    result = serialize_entity(entity)
    expected = {"type": "pre", "offset": 0, "length": 10}
    assert result == expected


def test_serialize_url_entity() -> None:
    """Test serializing a url entity."""
    entity = MessageEntityUrl(offset=15, length=12)
    result = serialize_entity(entity)
    expected = {"type": "url", "offset": 15, "length": 12}
    assert result == expected


def test_serialize_text_url_entity() -> None:
    """Test serializing a text_url entity with url."""
    entity = MessageEntityTextUrl(offset=0, length=5, url="https://example.com")
    result = serialize_entity(entity)
    expected = {"type": "text_url", "offset": 0, "length": 5, "url": "https://example.com"}
    assert result == expected


def test_serialize_spoiler_entity() -> None:
    """Test serializing a spoiler entity."""
    entity = MessageEntitySpoiler(offset=7, length=4)
    result = serialize_entity(entity)
    expected = {"type": "spoiler", "offset": 7, "length": 4}
    assert result == expected


def test_serialize_unsupported_entity_returns_none() -> None:
    """Test that unsupported entity types return None."""
    entity = MessageEntityMention(offset=0, length=5)
    result = serialize_entity(entity)
    assert result is None


def test_serialize_entities_none_input() -> None:
    """Test serialize_entities with None input."""
    result = serialize_entities(None)
    assert result == []


def test_serialize_entities_empty_list() -> None:
    """Test serialize_entities with empty list."""
    result = serialize_entities([])
    assert result == []


def test_serialize_entities_mixed_types() -> None:
    """Test serialize_entities with mixed supported and unsupported types."""
    entities = [
        MessageEntityBold(offset=0, length=4),
        MessageEntityMention(offset=5, length=8),  # unsupported
        MessageEntityItalic(offset=10, length=3),
    ]
    result = serialize_entities(entities)
    expected = [
        {"type": "bold", "offset": 0, "length": 4},
        {"type": "italic", "offset": 10, "length": 3},
    ]
    assert result == expected


def test_serialize_entities_multiple() -> None:
    """Test serialize_entities with multiple supported types."""
    entities = [
        MessageEntityBold(offset=0, length=5),
        MessageEntityItalic(offset=6, length=4),
        MessageEntityTextUrl(offset=11, length=7, url="https://test.com"),
    ]
    result = serialize_entities(entities)
    expected = [
        {"type": "bold", "offset": 0, "length": 5},
        {"type": "italic", "offset": 6, "length": 4},
        {"type": "text_url", "offset": 11, "length": 7, "url": "https://test.com"},
    ]
    assert result == expected


@pytest.mark.asyncio
async def test_serialize_message_with_entities() -> None:
    """Test serialize_message includes entities from message."""
    file_store = FileStore()
    message = _create_mock_message(123, "Hello world", [MessageEntityBold(offset=0, length=5)])
    result = await serialize_message(message, file_store)
    assert result.type == "text"
    assert result.text == "Hello world"
    assert result.message_id == 123
    assert len(result.entities) == 1
    assert result.entities[0] == {"type": "bold", "offset": 0, "length": 5}


@pytest.mark.asyncio
async def test_serialize_message_without_entities() -> None:
    """Test serialize_message with message that has no entities."""
    file_store = FileStore()
    message = _create_mock_message(456, "Plain text", None)
    result = await serialize_message(message, file_store)
    assert result.type == "text"
    assert result.text == "Plain text"
    assert result.message_id == 456
    assert result.entities == []
