"""Reproduce GitHub issue #25: click() returns ServerlessMessage instead of BotCallbackAnswer.

In Telethon, Message.click(data=...) sends a GetBotCallbackAnswerRequest and
returns a BotCallbackAnswer.  Any messages the bot emits during callback
processing (via bot.send_message / reply_text) remain in the conversation
and are retrieved with conv.get_response().

In the serverless client, click() runs the callback handler, drains the
outbox of all new responses, and returns the last one as a
ServerlessMessage.  This means:
  1. Return type differs (ServerlessMessage vs BotCallbackAnswer-like).
  2. get_response() after click() finds nothing — the message was consumed.
"""

import pytest
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from tg_auto_test.test_utils.models import ServerlessMessage
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


async def _inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Go", callback_data="go")],
        ])
        await update.message.reply_text("Pick:", reply_markup=keyboard)


async def _callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mimics a real bot: answer the callback, then send a new message."""
    del context
    if not update.callback_query:
        return
    await update.callback_query.answer()
    if update.callback_query.message:
        await update.callback_query.message.reply_text("Confirmed!")


def _build_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(CommandHandler("menu", _inline_handler))
    app.add_handler(CallbackQueryHandler(_callback_handler))
    return app


@pytest.mark.asyncio
async def test_click_return_type_is_not_serverless_message() -> None:
    """click(data=...) must NOT return a ServerlessMessage.

    Telethon returns a BotCallbackAnswer (or None on timeout).
    Our serverless fake currently returns a ServerlessMessage, which
    breaks the contract.
    """
    client = ServerlessTelegramClient(build_application=_build_app)
    await client.connect()
    try:
        async with client.conversation("bot") as conv:
            await conv.send_message("/menu")
            msg = await conv.get_response()

            result = await msg.click(data=b"go")

            assert not isinstance(result, ServerlessMessage), (
                "click() returned ServerlessMessage; Telethon returns BotCallbackAnswer"
            )
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_click_does_not_consume_outbox() -> None:
    """After click(), the bot's response must still be available via get_response().

    Telethon's click() only sends the callback query acknowledgement;
    the actual message the bot sends is a separate event retrievable
    through conv.get_response().
    """
    client = ServerlessTelegramClient(build_application=_build_app)
    await client.connect()
    try:
        async with client.conversation("bot") as conv:
            await conv.send_message("/menu")
            msg = await conv.get_response()

            await msg.click(data=b"go")

            confirmation = await conv.get_response()
            assert "confirmed" in confirmation.text.lower()
    finally:
        await client.disconnect()
