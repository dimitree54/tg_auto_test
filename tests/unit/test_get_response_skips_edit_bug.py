"""Reproduce GitHub issue #26: get_response() returns editMessageText after click().

In real Telethon, ``conv.get_response()`` only returns messages from
``NewMessage`` events (i.e. ``sendMessage``).  An ``editMessageText``
is an ``EditMessage`` event and should only be accessible through
``conv.get_edit()``.

The bot callback handler under test performs three steps:
  1. ``query.answer()`` → ``answerCallbackQuery``
  2. ``query.message.edit_text(text, reply_markup=None)`` → ``editMessageText``
  3. ``bot.send_message(chat_id, text)`` → ``sendMessage``

After ``click()``, ``get_response()`` should return the ``sendMessage``
from step 3.  Instead, it returns the ``editMessageText`` from step 2
because ``_replace_edited_message()`` appends the edit to the main
outbox when the original message has already been consumed.
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

MENU_TEXT = "Choose an option:"
CONFIRMATION_TEXT = "Added!"


async def _menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.message:
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Add item", callback_data="add")],
    ])
    await update.message.reply_text(MENU_TEXT, reply_markup=keyboard)


async def _callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mimics a real bot: answer → edit keyboard away → send confirmation."""
    del context
    query = update.callback_query
    if not query:
        return
    await query.answer()
    if query.message:
        await query.message.edit_text(query.message.text, reply_markup=None)
    chat_id = update.effective_chat.id if update.effective_chat else 0
    await query.get_bot().send_message(chat_id=chat_id, text=CONFIRMATION_TEXT)


def _build_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(CommandHandler("menu", _menu_handler))
    app.add_handler(CallbackQueryHandler(_callback_handler))
    return app


@pytest.mark.asyncio
async def test_get_response_returns_send_message_not_edit() -> None:
    """get_response() after click() must return the sendMessage, not the editMessageText.

    The bug: ``_replace_edited_message()`` appends the edit to the main
    outbox when the original has already been consumed by an earlier
    ``get_response()``.  This causes the next ``get_response()`` to pop
    the edit instead of the confirmation ``sendMessage``.
    """
    client = ServerlessTelegramClient(build_application=_build_app)
    await client.connect()
    try:
        async with client.conversation("bot") as conv:
            await conv.send_message("/menu")
            menu_msg = await conv.get_response()
            assert menu_msg.text == MENU_TEXT

            await menu_msg.click(data=b"add")

            confirmation = await conv.get_response()
            assert confirmation.text == CONFIRMATION_TEXT, (
                f"get_response() returned '{confirmation.text}' "
                f"(likely the editMessageText) instead of '{CONFIRMATION_TEXT}'"
            )
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_edit_lands_in_edit_outbox() -> None:
    """The editMessageText must be accessible via get_edit().

    After click(), the callback handler's edit_text() call produces an
    editMessageText that must land in the edit outbox, retrievable via
    get_edit() — not only in the main outbox.
    """
    client = ServerlessTelegramClient(build_application=_build_app)
    await client.connect()
    try:
        async with client.conversation("bot") as conv:
            await conv.send_message("/menu")
            menu_msg = await conv.get_response()

            await menu_msg.click(data=b"add")

            edited = await conv.get_edit()
            assert edited.id == menu_msg.id, (
                f"get_edit() should return the edited menu message (id={menu_msg.id}), got message with id={edited.id}"
            )
    finally:
        await client.disconnect()
