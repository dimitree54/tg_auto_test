from tg_auto_test.test_utils.json_types import JsonValue
from tg_auto_test.test_utils.markdown_v2_tokens import (
    MARKERS,
    RESERVED,
    code_content,
    link_entity,
    read_escape,
    read_until,
)


class MarkdownV2Parser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.position = 0
        self.offset = 0
        self.pieces: list[str] = []
        self.entities: list[dict[str, JsonValue]] = []
        self.active: list[str] = []
        self.in_link = False

    def parse(self, closing: str | None = None) -> None:
        while self.position < len(self.text):
            if closing is not None and self.text.startswith(closing, self.position):
                self.position += len(closing)
                return
            char = self.text[self.position]
            if char == "\\":
                literal, self.position = read_escape(self.text, self.position)
                self.append(literal)
            elif char == "\r":
                self.position += 1
            elif char == "`":
                self.parse_code()
            elif self.text.startswith("![", self.position) or char == "[":
                self.parse_link()
            elif char == ">" and (not self.pieces or self.pieces[-1].endswith("\n")):
                self.parse_quote()
            elif marker := next((value for value in MARKERS if self.text.startswith(value, self.position)), None):
                if marker in self.active:
                    raise ValueError("Overlapping MarkdownV2 formatting")
                self.position += len(marker)
                start = self.offset
                self.active.append(marker)
                self.parse(marker)
                self.active.pop()
                self.add_entity({"type": MARKERS[marker]}, start)
            elif char in RESERVED:
                raise ValueError(f"Unescaped MarkdownV2 character: {char}")
            else:
                self.append(char)
                self.position += 1
        if closing is not None:
            raise ValueError(f"Unclosed MarkdownV2 delimiter: {closing}")

    def append(self, text: str) -> None:
        self.pieces.append(text)
        self.offset += len(text.encode("utf-16-le")) // 2

    def add_entity(self, data: dict[str, JsonValue], start: int) -> None:
        if self.offset > start:
            self.entities.append({**data, "offset": start, "length": self.offset - start})

    def parse_code(self) -> None:
        if self.active:
            raise ValueError("MarkdownV2 code cannot be nested in formatting")
        pre = self.text.startswith("```", self.position)
        content, language, self.position = code_content(self.text, self.position)
        start = self.offset
        self.append(content)
        data: dict[str, JsonValue] = {"type": "pre" if pre else "code"}
        if language:
            data["language"] = language
        self.add_entity(data, start)

    def parse_link(self) -> None:
        if self.in_link:
            raise ValueError("MarkdownV2 links cannot be nested")
        custom = self.text.startswith("![", self.position)
        self.position += 2 if custom else 1
        start = self.offset
        self.in_link = True
        self.parse("]")
        self.in_link = False
        if self.offset == start:
            raise ValueError("MarkdownV2 link label must not be empty")
        if not self.text.startswith("(", self.position):
            raise ValueError("MarkdownV2 link must include a target")
        target, self.position = read_until(self.text, self.position + 1, ")")
        self.add_entity(link_entity(target, custom), start)

    def parse_quote(self) -> None:
        start = self.offset
        lines: list[str] = []
        while self.position < len(self.text) and self.text[self.position] == ">":
            end = self.text.find("\n", self.position)
            end = len(self.text) if end == -1 else end
            lines.append(self.text[self.position + 1 : end])
            self.position = end
            if end + 1 >= len(self.text) or self.text[end + 1] != ">":
                break
            self.position += 1
        source = "\n".join(lines)
        expandable = source.endswith("||") and source.count("||") % 2 == 1
        if expandable:
            source = source[:-2]
        plain, entities = parse_markdown_v2(source)
        if any(entity["type"] in ("blockquote", "expandable_blockquote") for entity in entities):
            raise ValueError("MarkdownV2 blockquotes cannot be nested")
        self.append(plain)
        self.entities.extend({**entity, "offset": int(entity["offset"]) + start} for entity in entities)
        self.add_entity({"type": "expandable_blockquote" if expandable else "blockquote"}, start)


def parse_markdown_v2(text: str) -> tuple[str, list[dict[str, JsonValue]]]:
    parser = MarkdownV2Parser(text)
    parser.parse()
    parser.entities.sort(key=lambda entity: (int(entity["offset"]), -int(entity["length"])))
    return "".join(parser.pieces), parser.entities
