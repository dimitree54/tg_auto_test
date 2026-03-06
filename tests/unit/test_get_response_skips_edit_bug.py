"""Reproduce GitHub issue #26: get_response() returns editMessageText after click().

After click(), the callback handler may:
  1. answer() → answerCallbackQuery
  2. edit_text(..., reply_markup=None) → editMessageText (removes keyboard)
  3. send_message(...) → sendMessage (confirmation)

In real Telethon, get_response() only matches NewMessage events.  The
editMessageText triggers an EditMessage event which get_response() ignores.

In the serverless client, _replace_edited_message() fell back to appending
the edit to _outbox when the original message was no longer there (already
consumed by a prior get_response()).  This caused get_response() to return
the edit (with empty text and _is_edit=True) instead of the sendMessage.
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

from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


async def _inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Add", callback_data="add")],
        ])
        await update.message.reply_text("Choose:", reply_markup=keyboard)


async def _callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mimics a real bot: answer, remove keyboard via edit, then send confirmation."""
    if not update.callback_query:
        return
    query = update.callback_query
    await query.answer()
    # Step 2: edit the original message to remove the keyboard
    if query.message:
        await query.message.edit_text(query.message.text or "", reply_markup=None)
    # Step 3: send a new confirmation message
    if context.bot and query.message:
        await context.bot.send_message(query.message.chat_id, text="Added!")


def _build_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(CommandHandler("menu", _inline_handler))
    app.add_handler(CallbackQueryHandler(_callback_handler))
    return app


@pytest.mark.asyncio
async def test_get_response_returns_send_message_not_edit() -> None:
    """get_response() after click() must return the sendMessage, not the editMessageText.

    The callback handler does:
      1. answer() → answerCallbackQuery
      2. edit_text(reply_markup=None) → editMessageText (removes keyboard)
      3. send_message("Added!") → sendMessage (confirmation)

    get_response() must return the confirmation from step 3, not the edit from step 2.
    """
    client = ServerlessTelegramClient(build_application=_build_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/menu")
            msg_with_buttons = await conv.get_response()

            assert msg_with_buttons.text == "Choose:"
            assert msg_with_buttons.buttons is not None

            await msg_with_buttons.click(data=b"add")
            confirmation = await conv.get_response()

            assert confirmation.text == "Added!", (
                f"Expected 'Added!' but got '{confirmation.text}'. "
                "get_response() returned the editMessageText instead of sendMessage."
            )
            assert not confirmation._is_edit, (  # noqa: SLF001
                "get_response() returned an edit (is_edit=True) — "
                "it must only return new messages."
            )
    finally:
        await client.disconnect()
