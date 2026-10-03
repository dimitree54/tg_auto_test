from tg_auto_test.test_utils.json_types import JsonValue

MARKERS = {"__": "underline", "||": "spoiler", "*": "bold", "_": "italic", "~": "strikethrough"}
RESERVED = frozenset("_*[]()~`>#+-=|{}.!")


def read_escape(text: str, position: int) -> tuple[str, int]:
    if position + 1 >= len(text) or not 1 <= ord(text[position + 1]) <= 126:
        raise ValueError("Invalid MarkdownV2 escape")
    return text[position + 1], position + 2


def read_until(text: str, position: int, closing: str) -> tuple[str, int]:
    parts: list[str] = []
    while position < len(text):
        if text.startswith(closing, position):
            return "".join(parts), position + len(closing)
        if text[position] == "\\":
            char, position = read_escape(text, position)
            parts.append(char)
        else:
            parts.append(text[position])
            position += 1
    raise ValueError(f"Unclosed MarkdownV2 delimiter: {closing}")


def code_content(text: str, position: int) -> tuple[str, str, int]:
    marker = "```" if text.startswith("```", position) else "`"
    content, end = read_until(text, position + len(marker), marker)
    language = ""
    if marker == "```" and "\n" in content:
        header, body = content.split("\n", 1)
        if not header or all(char.isalnum() or char in "_+-#." for char in header):
            language, content = header, body
    return content, language, end


def link_entity(target: str, custom_emoji: bool) -> dict[str, JsonValue]:
    if custom_emoji:
        prefix = "tg://emoji?id="
        if not target.startswith(prefix) or not target[len(prefix) :].isdigit():
            raise NotImplementedError("Unsupported MarkdownV2 custom entity target")
        return {"type": "custom_emoji", "custom_emoji_id": target[len(prefix) :]}
    if target.startswith("tg://user?"):
        raise NotImplementedError("MarkdownV2 user mentions require user resolution")
    if not target:
        raise ValueError("MarkdownV2 link target must not be empty")
    return {"type": "text_link", "url": target}
