import pytest
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters
from telethon.tl.types import MessageEntityBold, MessageEntityTextUrl

from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["send", "edit", "caption"])
async def test_formatted_bot_api_responses_match_telegram(operation: str) -> None:
    async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        assert update.message is not None
        text = r"📚 *[Обзор🧠](https://example.com/review)* https://example\.com/path?source\=telegram"
        if operation == "send":
            await update.message.reply_text(text, parse_mode="MarkdownV2")
        elif operation == "edit":
            message = await update.message.reply_text("loading")
            await message.edit_text(text, parse_mode="MarkdownV2")
        else:
            await update.message.reply_document(b"fixture", caption=text, parse_mode="MarkdownV2")

    def build_app(builder: ApplicationBuilder) -> Application:
        app = builder.build()
        app.add_handler(MessageHandler(filters.TEXT, reply))
        return app

    client = ServerlessTelegramClient(build_application=build_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("hi")
            result = await conv.get_edit() if operation == "edit" else await conv.get_response()
        assert result.text == "📚 Обзор🧠 https://example.com/path?source=telegram"
        assert {type(entity) for entity in result.entities} == {MessageEntityBold, MessageEntityTextUrl}
        assert all(entity.offset == 3 and entity.length == 7 for entity in result.entities)
        link = next(entity for entity in result.entities if isinstance(entity, MessageEntityTextUrl))
        assert link.url == "https://example.com/review"
    finally:
        await client.disconnect()
