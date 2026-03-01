"""Parse Telegram Bot API HTML into plain text and entity dicts.

The real Telegram Bot API accepts HTML-formatted text and returns:
  - ``text``: the plain text with all HTML tags stripped
  - ``entities``: a list of entity dicts describing the formatting

This module replicates that behavior so the stub can produce correct API
responses when ``parse_mode=HTML`` is used.

Supported tags: <b>, <strong>, <i>, <em>, <u>, <ins>, <s>, <strike>, <del>,
<code>, <pre>, <a href="...">, <span class="tg-spoiler">, <tg-spoiler>.
"""

from html.parser import HTMLParser

from tg_auto_test.test_utils.json_types import JsonValue

_TAG_TO_ENTITY_TYPE: dict[str, str] = {
    "b": "bold",
    "strong": "bold",
    "i": "italic",
    "em": "italic",
    "u": "underline",
    "ins": "underline",
    "s": "strikethrough",
    "strike": "strikethrough",
    "del": "strikethrough",
    "code": "code",
    "pre": "pre",
    "a": "text_url",
    "tg-spoiler": "spoiler",
}


def _build_entity(tag: str, offset: int, length: int, attrs: dict[str, str]) -> dict[str, JsonValue] | None:
    if tag == "span":
        if attrs.get("class") != "tg-spoiler":
            return None
        return {"type": "spoiler", "offset": offset, "length": length}

    entity_type = _TAG_TO_ENTITY_TYPE.get(tag)
    if entity_type is None:
        return None

    result: dict[str, JsonValue] = {"type": entity_type, "offset": offset, "length": length}
    if entity_type == "text_url":
        result["url"] = attrs.get("href", "")
    if entity_type == "pre" and attrs.get("language"):
        result["language"] = attrs["language"]
    return result


class _TelegramHTMLParser(HTMLParser):
    """Parser that strips HTML tags and collects entity dicts."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._pieces: list[str] = []
        self._offset = 0
        self._stack: list[tuple[str, int, dict[str, str]]] = []
        self._entities: list[dict[str, JsonValue]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_dict = {k: (v or "") for k, v in attrs}
        self._stack.append((tag, self._offset, attr_dict))

    def handle_endtag(self, tag: str) -> None:
        for i in range(len(self._stack) - 1, -1, -1):
            open_tag, start_offset, attrs = self._stack[i]
            if open_tag == tag:
                self._stack.pop(i)
                length = self._offset - start_offset
                if length > 0:
                    entity = _build_entity(tag, start_offset, length, attrs)
                    if entity is not None:
                        self._entities.append(entity)
                return

    def handle_data(self, data: str) -> None:
        self._pieces.append(data)
        self._offset += len(data)

    def result(self) -> tuple[str, list[dict[str, JsonValue]]]:
        return "".join(self._pieces), self._entities


def parse_html(html_text: str) -> tuple[str, list[dict[str, JsonValue]]]:
    """Parse Telegram HTML markup into plain text and entity dicts.

    Returns:
        Tuple of (plain_text, entities) in Telegram Bot API format, sorted by offset.
    """
    parser = _TelegramHTMLParser()
    parser.feed(html_text)
    text, entities = parser.result()
    entities.sort(key=lambda e: int(e.get("offset", 0)))
    return text, entities
