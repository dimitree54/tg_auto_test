"""Convert Telegram Bot API entity dicts to Telethon entity objects."""

from telethon.tl.types import (
    MessageEntityBlockquote,
    MessageEntityBold,
    MessageEntityCode,
    MessageEntityCustomEmoji,
    MessageEntityItalic,
    MessageEntityPre,
    MessageEntitySpoiler,
    MessageEntityStrike,
    MessageEntityTextUrl,
    MessageEntityUnderline,
)

from tg_auto_test.test_utils.json_types import JsonValue

_SIMPLE_ENTITY_TYPES: dict[str, type] = {
    "bold": MessageEntityBold,
    "italic": MessageEntityItalic,
    "underline": MessageEntityUnderline,
    "strikethrough": MessageEntityStrike,
    "code": MessageEntityCode,
    "spoiler": MessageEntitySpoiler,
}


def convert_entity(entity_dict: dict[str, JsonValue]) -> object | None:
    """Convert a single Telegram Bot API entity dict to a Telethon entity object."""
    entity_type = entity_dict.get("type")
    if not isinstance(entity_type, str):
        return None
    offset = int(entity_dict["offset"])
    length = int(entity_dict["length"])

    simple_cls = _SIMPLE_ENTITY_TYPES.get(entity_type)
    if simple_cls is not None:
        return simple_cls(offset=offset, length=length)
    if entity_type == "pre":
        return MessageEntityPre(offset=offset, length=length, language=str(entity_dict.get("language", "")))
    if entity_type == "text_link":
        return MessageEntityTextUrl(offset=offset, length=length, url=str(entity_dict.get("url", "")))
    if entity_type in ("blockquote", "expandable_blockquote"):
        return MessageEntityBlockquote(offset=offset, length=length, collapsed=entity_type == "expandable_blockquote")
    if entity_type == "custom_emoji":
        return MessageEntityCustomEmoji(offset=offset, length=length, document_id=int(entity_dict["custom_emoji_id"]))
    return None


def convert_entities(entity_dicts: list[dict[str, JsonValue]]) -> list[object]:
    """Convert a list of Telegram Bot API entity dicts to Telethon entity objects."""
    result = []
    for entity_dict in entity_dicts:
        entity = convert_entity(entity_dict)
        if entity is not None:
            result.append(entity)
    return result
