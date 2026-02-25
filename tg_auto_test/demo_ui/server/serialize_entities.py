"""Entity serialization utilities for converting Telethon entities to API format."""

from telethon.tl.types import (
    MessageEntityBold,
    MessageEntityCode,
    MessageEntityItalic,
    MessageEntityPre,
    MessageEntitySpoiler,
    MessageEntityStrike,
    MessageEntityTextUrl,
    MessageEntityUnderline,
    MessageEntityUrl,
)

ENTITY_TYPE_MAP: dict[type, str] = {
    MessageEntityBold: "bold",
    MessageEntityItalic: "italic",
    MessageEntityUnderline: "underline",
    MessageEntityStrike: "strikethrough",
    MessageEntityCode: "code",
    MessageEntityPre: "pre",
    MessageEntityUrl: "url",
    MessageEntityTextUrl: "text_url",
    MessageEntitySpoiler: "spoiler",
}


def serialize_entity(entity: object) -> dict[str, str | int] | None:
    """Serialize a single Telethon entity to API format.

    Args:
        entity: Telethon MessageEntity object

    Returns:
        Dictionary with type, offset, length and optional url/language,
        or None if entity type is unsupported
    """
    entity_type = ENTITY_TYPE_MAP.get(type(entity))
    if entity_type is None:
        return None

    result = {
        "type": entity_type,
        "offset": entity.offset,
        "length": entity.length,
    }

    if entity_type == "text_url":
        result["url"] = entity.url
    elif entity_type == "pre" and getattr(entity, "language", None):
        result["language"] = entity.language

    return result


def serialize_entities(entities: list[object] | None) -> list[dict[str, str | int]]:
    """Serialize a list of Telethon entities to API format.

    Args:
        entities: List of Telethon MessageEntity objects or None

    Returns:
        List of serialized entity dictionaries (unsupported types are filtered out)
    """
    if not entities:
        return []

    serialized = []
    for entity in entities:
        serialized_entity = serialize_entity(entity)
        if serialized_entity is not None:
            serialized.append(serialized_entity)

    return serialized
