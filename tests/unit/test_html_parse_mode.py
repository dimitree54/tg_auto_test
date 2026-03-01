"""Tests for HTML parse_mode support in the serverless testing infrastructure."""

import pytest
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes
from telethon.tl.types import (
    MessageEntityBold,
    MessageEntityCode,
    MessageEntityItalic,
    MessageEntityPre,
    MessageEntitySpoiler,
    MessageEntityStrike,
    MessageEntityTextUrl,
    MessageEntityUnderline,
)

from tests.unit.html_test_app import build_html_app
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient

_SIMPLE_ENTITY_CASES = [
    ("bold", "<b>bold</b>", "bold", MessageEntityBold, 4),
    ("italic", "<i>italic</i>", "italic", MessageEntityItalic, 6),
    ("underline", "<u>underline</u>", "underline", MessageEntityUnderline, 9),
    ("strike", "<s>strikethrough</s>", "strikethrough", MessageEntityStrike, 13),
    ("code", "<code>inline code</code>", "inline code", MessageEntityCode, 11),
    ("pre", "<pre>code block</pre>", "code block", MessageEntityPre, 10),
    ("spoiler", '<span class="tg-spoiler">spoiler</span>', "spoiler", MessageEntitySpoiler, 7),
    ("tgspoiler", "<tg-spoiler>spoiler</tg-spoiler>", "spoiler", MessageEntitySpoiler, 7),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("command", "html", "expected_text", "entity_cls", "length"),
    _SIMPLE_ENTITY_CASES,
    ids=[c[0] for c in _SIMPLE_ENTITY_CASES],
)
async def test_simple_html_entity(command: str, html: str, expected_text: str, entity_cls: type, length: int) -> None:
    """Bot sends a single HTML tag -> text is stripped, correct entity is produced."""
    del html  # documented for clarity; the bot handler uses it internally
    client = ServerlessTelegramClient(build_application=build_html_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message(f"/{command}")
            msg = await conv.get_response()
        assert msg.text == expected_text
        assert len(msg.entities) == 1
        assert isinstance(msg.entities[0], entity_cls)
        assert msg.entities[0].offset == 0
        assert msg.entities[0].length == length
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_link_html() -> None:
    """Bot sends <a href="url">link</a> -> text_url entity with correct URL."""
    client = ServerlessTelegramClient(build_application=build_html_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/link")
            msg = await conv.get_response()
        assert msg.text == "link"
        assert len(msg.entities) == 1
        assert isinstance(msg.entities[0], MessageEntityTextUrl)
        assert msg.entities[0].offset == 0
        assert msg.entities[0].length == 4
        assert msg.entities[0].url == "https://example.com"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_nested_bold_italic_html() -> None:
    """Bot sends <b><i>bold italic</i></b> -> two overlapping entities."""
    client = ServerlessTelegramClient(build_application=build_html_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/nested")
            msg = await conv.get_response()
        assert msg.text == "bold italic"
        entity_types = {type(e) for e in msg.entities}
        assert MessageEntityBold in entity_types
        assert MessageEntityItalic in entity_types
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_mixed_text_and_html() -> None:
    """Bot sends 'Send <b>text</b> or <b>photo</b>' -> plain text with bold entities."""
    client = ServerlessTelegramClient(build_application=build_html_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/mixed")
            msg = await conv.get_response()
        assert msg.text == "Send text or photo to translate."
        assert len(msg.entities) == 2
        assert all(isinstance(e, MessageEntityBold) for e in msg.entities)
        assert msg.entities[0].offset == 5
        assert msg.entities[0].length == 4
        assert msg.entities[1].offset == 13
        assert msg.entities[1].length == 5
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_multiline_html() -> None:
    """Bot sends HTML with newlines -> newlines preserved in plain text."""

    async def _multiline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        if update.message:
            await update.message.reply_text(
                "📝 <b>Распознанный текст:</b>\nocr\n\n🔄 <b>Перевод:</b>\ntranslation",
                parse_mode="HTML",
            )

    def _build_app(builder: ApplicationBuilder) -> Application:
        app = builder.build()
        app.add_handler(CommandHandler("multi", _multiline_handler))
        return app

    client = ServerlessTelegramClient(build_application=_build_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/multi")
            msg = await conv.get_response()
        assert "📝 Распознанный текст:\nocr\n\n🔄 Перевод:\ntranslation" == msg.text
        assert len(msg.entities) == 2
        assert all(isinstance(e, MessageEntityBold) for e in msg.entities)
    finally:
        await client.disconnect()
