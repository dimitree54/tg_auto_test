import pytest

from tg_auto_test.test_utils.markdown_v2_parser import parse_markdown_v2


@pytest.mark.parametrize(
    "source,plain,entity_type",
    [
        ("*bold*", "bold", "bold"),
        ("_italic_", "italic", "italic"),
        ("__underline__", "underline", "underline"),
        ("~strike~", "strike", "strikethrough"),
        ("||spoiler||", "spoiler", "spoiler"),
        (r"`a\`b\\c`", "a`b\\c", "code"),
        ("```python\nx = 1\n```", "x = 1\n", "pre"),
        (">first\n>second", "first\nsecond", "blockquote"),
        (">first\n>hidden||", "first\nhidden", "expandable_blockquote"),
    ],
)
def test_markdown_v2_entities(source: str, plain: str, entity_type: str) -> None:
    text, entities = parse_markdown_v2(source)
    assert text == plain
    assert entities[0]["type"] == entity_type
    assert entities[0]["offset"] == 0
    assert entities[0]["length"] == len(plain.encode("utf-16-le")) // 2


def test_escaped_url_is_rendered_without_backslashes() -> None:
    text, entities = parse_markdown_v2(r"https://example\.com/review?source\=telegram")
    assert text == "https://example.com/review?source=telegram"
    assert entities == []


def test_nested_formatting_link_and_utf16_offsets() -> None:
    text, entities = parse_markdown_v2(r"📚 *[Обзор🧠](https://example.com/a_(b\))*")
    assert text == "📚 Обзор🧠"
    assert {entity["type"] for entity in entities} == {"bold", "text_link"}
    assert all(entity["offset"] == 3 and entity["length"] == 7 for entity in entities)
    link = next(entity for entity in entities if entity["type"] == "text_link")
    assert link["url"] == "https://example.com/a_(b)"


def test_underline_ambiguity_with_empty_bold_separator() -> None:
    text, entities = parse_markdown_v2("___both_**__")
    assert text == "both"
    assert {entity["type"] for entity in entities} == {"italic", "underline"}


def test_custom_emoji() -> None:
    text, entities = parse_markdown_v2("![👍](tg://emoji?id=5368324170671202286)")
    assert text == "👍"
    assert entities == [{"type": "custom_emoji", "custom_emoji_id": "5368324170671202286", "offset": 0, "length": 2}]


@pytest.mark.parametrize(
    "source",
    [
        "unescaped!",
        "*unclosed",
        "[no target]",
        "text\\",
        "*`nested`*",
        "*a _b* c_",
        "[](https://example.com)",
        "[outer [inner](https://example.com)](https://example.com)",
        ">>nested",
    ],
)
def test_malformed_markdown_v2_fails(source: str) -> None:
    with pytest.raises(ValueError):
        parse_markdown_v2(source)
