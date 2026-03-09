"""Reproduce GitHub issue #29: non-blocking handlers may reply later."""

import asyncio

import pytest
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters

from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient

_DELAY_SECONDS = 0.05


async def _delayed_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.message:
        return
    await asyncio.sleep(_DELAY_SECONDS)
    await update.message.reply_text("Done!")


def _build_non_blocking_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _delayed_reply_handler, block=False))
    return app


@pytest.mark.asyncio
async def test_send_message_allows_block_false_handler_to_reply_later() -> None:
    client = ServerlessTelegramClient(build_application=_build_non_blocking_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("hello")
            response = await conv.get_response()
            assert response.text == "Done!"
    finally:
        await client.disconnect()
