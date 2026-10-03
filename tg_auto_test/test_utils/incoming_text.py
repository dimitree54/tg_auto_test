from telethon.tl.types import TypeMessageEntity
from telethon.utils import sanitize_parse_mode

from tg_auto_test.test_utils.incoming_entities import incoming_entity
from tg_auto_test.test_utils.json_types import JsonValue


def apply_incoming_text(
    message: dict[str, JsonValue],
    text: str,
    *,
    caption: bool = False,
    parse_mode: object = (),
    formatting_entities: list[TypeMessageEntity] | None = None,
) -> str:
    if formatting_entities is None:
        parser = sanitize_parse_mode("md" if parse_mode == () else parse_mode)
        visible_text, entities = (text, []) if parser is None else parser.parse(text)
    else:
        visible_text, entities = text, formatting_entities
    bot_entities = [incoming_entity(entity) for entity in entities]
    if visible_text.startswith("/") and not any(entity["type"] == "bot_command" for entity in bot_entities):
        command = visible_text.split(maxsplit=1)[0]
        bot_entities.insert(0, {"type": "bot_command", "offset": 0, "length": len(command.encode("utf-16-le")) // 2})
    text_key, entities_key = ("caption", "caption_entities") if caption else ("text", "entities")
    message[text_key] = visible_text
    message[entities_key] = bot_entities
    return visible_text
