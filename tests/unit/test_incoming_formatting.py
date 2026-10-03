from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from telegram import Message, Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters
from telethon.tl.types import MessageEntityTextUrl

from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


@pytest_asyncio.fixture
async def incoming_client() -> AsyncIterator[tuple[ServerlessTelegramClient, list[Message]]]:
    received: list[Message] = []

    async def record(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        assert update.message is not None
        received.append(update.message)
        await update.message.reply_text("received")

    def build_app(builder: ApplicationBuilder) -> Application:
        app = builder.build()
        app.add_handler(MessageHandler(filters.ALL, record))
        return app

    client = ServerlessTelegramClient(build_application=build_app)
    await client.connect()
    yield client, received
    await client.disconnect()


@pytest.mark.asyncio
@pytest.mark.parametrize("conversation", [False, True], ids=["client", "conversation"])
@pytest.mark.parametrize("caption", [False, True], ids=["text", "caption"])
@pytest.mark.parametrize("mode", ["default", "md", "html", "explicit"])
async def test_hidden_links_have_bot_api_entities(
    incoming_client: tuple[ServerlessTelegramClient, list[Message]], conversation: bool, caption: bool, mode: str
) -> None:
    client, received = incoming_client
    url = "https://example.com/review?full=1"
    text = f"📚 [Обзор🧠]({url})!"
    options: dict[str, object] = {}
    if mode == "html":
        text = f'📚 <a href="{url}">Обзор🧠</a>!'
        options["parse_mode"] = "html"
    elif mode == "md":
        options["parse_mode"] = "md"
    elif mode == "explicit":
        text = "📚 Обзор🧠!"
        options.update(parse_mode="invalid", formatting_entities=[MessageEntityTextUrl(3, 7, url)])
    async with client.conversation("test_bot") as conv:
        sender = conv if conversation else client
        args = () if conversation else (9001,)
        if caption:
            await sender.send_file(*args, b"fixture", caption=text, force_document=True, **options)
        else:
            await sender.send_message(*args, text, **options)
        assert (await conv.get_response()).text == "received"
    message = received[0]
    visible = message.caption if caption else message.text
    entities = message.caption_entities if caption else message.entities
    assert visible == "📚 Обзор🧠!"
    assert len(entities) == 1
    assert entities[0].type == "text_link"
    assert entities[0].url == url
    assert entities[0].offset == 3
    assert entities[0].length == 7


@pytest.mark.asyncio
@pytest.mark.parametrize("options", [{"parse_mode": None}, {"formatting_entities": []}])
async def test_disabled_parsing_keeps_literal_markdown(
    incoming_client: tuple[ServerlessTelegramClient, list[Message]], options: dict[str, object]
) -> None:
    client, received = incoming_client
    text = "[literal](https://example.com)"
    await client.send_message(9001, text, **options)
    assert received[0].text == text
    assert received[0].entities == ()


@pytest.mark.asyncio
async def test_unknown_parse_mode_fails_before_dispatch(
    incoming_client: tuple[ServerlessTelegramClient, list[Message]],
) -> None:
    client, received = incoming_client
    with pytest.raises(ValueError, match="Unknown parse mode"):
        await client.send_message(9001, "text", parse_mode="invalid")
    assert received == []


@pytest.mark.asyncio
async def test_nested_formatting_and_multiple_links(
    incoming_client: tuple[ServerlessTelegramClient, list[Message]],
) -> None:
    client, received = incoming_client
    await client.send_message(
        9001,
        '<b><a href="https://example.com/1">first</a></b> <a href="https://example.com/2">second</a>',
        parse_mode="html",
    )
    assert received[0].text == "first second"
    links = received[0].parse_entities(types=["text_link"])
    assert [(label, entity.url) for entity, label in links.items()] == [
        ("first", "https://example.com/1"),
        ("second", "https://example.com/2"),
    ]
