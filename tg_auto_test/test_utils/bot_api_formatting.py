import json

from tg_auto_test.test_utils.html_parser import parse_html
from tg_auto_test.test_utils.json_types import JsonValue
from tg_auto_test.test_utils.markdown_v2_parser import parse_markdown_v2


def parse_bot_api_text(parameters: dict[str, str], text_key: str = "text") -> tuple[str, list[dict[str, JsonValue]]]:
    text = parameters[text_key]
    entities_key = "caption_entities" if text_key == "caption" else "entities"
    if entities_key in parameters:
        entities = json.loads(parameters[entities_key])
        if not isinstance(entities, list) or not all(isinstance(entity, dict) for entity in entities):
            raise ValueError("Bot API entities must be a list of objects")
        return text, entities
    mode = parameters["parse_mode"].lower() if "parse_mode" in parameters else ""
    if mode == "html":
        return parse_html(text)
    if mode == "markdownv2":
        return parse_markdown_v2(text)
    if not mode:
        return text, []
    raise NotImplementedError(f"Unsupported Bot API parse mode: {mode}")
