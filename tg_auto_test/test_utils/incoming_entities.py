from telethon.tl import types

from tg_auto_test.test_utils.json_types import JsonValue

_SIMPLE_TYPES = {
    types.MessageEntityBold: "bold",
    types.MessageEntityItalic: "italic",
    types.MessageEntityUnderline: "underline",
    types.MessageEntityStrike: "strikethrough",
    types.MessageEntitySpoiler: "spoiler",
    types.MessageEntityCode: "code",
    types.MessageEntityUrl: "url",
    types.MessageEntityEmail: "email",
    types.MessageEntityMention: "mention",
    types.MessageEntityHashtag: "hashtag",
    types.MessageEntityCashtag: "cashtag",
    types.MessageEntityPhone: "phone_number",
    types.MessageEntityBotCommand: "bot_command",
}


def incoming_entity(entity: types.TypeMessageEntity) -> dict[str, JsonValue]:
    result: dict[str, JsonValue] = {"offset": entity.offset, "length": entity.length}
    entity_class = type(entity)
    if entity_class in _SIMPLE_TYPES:
        result["type"] = _SIMPLE_TYPES[entity_class]
    elif isinstance(entity, types.MessageEntityTextUrl):
        result.update(type="text_link", url=entity.url)
    elif isinstance(entity, types.MessageEntityPre):
        result.update(type="pre", language=entity.language)
    elif isinstance(entity, types.MessageEntityBlockquote):
        result["type"] = "expandable_blockquote" if entity.collapsed else "blockquote"
    elif isinstance(entity, types.MessageEntityCustomEmoji):
        result.update(type="custom_emoji", custom_emoji_id=str(entity.document_id))
    else:
        raise NotImplementedError(f"Unsupported incoming entity: {entity_class.__name__}")
    return result
