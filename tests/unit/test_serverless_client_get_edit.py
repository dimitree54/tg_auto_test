"""Test get_edit() support in ServerlessTelegramConversation.

Verifies that the send-status-then-edit pattern (a common bot UX pattern)
works correctly in serverless mode:
  1. Bot sends an initial status message via sendMessage
  2. Bot edits that message via editMessageText
  3. conv.get_response() returns the original sendMessage
  4. conv.get_edit() returns the edited message
"""

import pytest
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, ApplicationBuilder, MessageHandler, filters, ContextTypes

from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


async def _status_then_edit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a status message, then edit it with a result and buttons."""
    del context
    if update.message:
        status = await update.message.reply_text("Processing...")
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Done", callback_data="done")],
        ])
        await status.edit_text("Result ready", reply_markup=keyboard)


async def _plain_edit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a status message, then edit it with plain text (no buttons)."""
    del context
    if update.message:
        status = await update.message.reply_text("Working...")
        await status.edit_text("Finished")


def _build_edit_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(MessageHandler(filters.Regex("^/edit_with_buttons$"), _status_then_edit_handler))
    app.add_handler(MessageHandler(filters.Regex("^/edit_plain$"), _plain_edit_handler))
    return app


@pytest.mark.asyncio
async def test_get_response_returns_original_message() -> None:
    """get_response() returns the initial sendMessage, not the edit."""
    client = ServerlessTelegramClient(build_application=_build_edit_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/edit_with_buttons")
            status = await conv.get_response()
            assert status.text == "Processing..."
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_get_edit_returns_edited_message() -> None:
    """get_edit() returns the editMessageText result."""
    client = ServerlessTelegramClient(build_application=_build_edit_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/edit_with_buttons")
            await conv.get_response()
            edited = await conv.get_edit()
            assert edited.text == "Result ready"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_get_edit_preserves_message_id() -> None:
    """The edited message keeps the same ID as the original."""
    client = ServerlessTelegramClient(build_application=_build_edit_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/edit_with_buttons")
            original = await conv.get_response()
            edited = await conv.get_edit()
            assert edited.id == original.id
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_get_edit_returns_buttons() -> None:
    """The edited message has the buttons attached via the edit."""
    client = ServerlessTelegramClient(build_application=_build_edit_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/edit_with_buttons")
            await conv.get_response()
            edited = await conv.get_edit()
            assert edited.buttons is not None
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_get_edit_plain_text() -> None:
    """get_edit() works for plain text edits without reply markup."""
    client = ServerlessTelegramClient(build_application=_build_edit_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/edit_plain")
            original = await conv.get_response()
            assert original.text == "Working..."
            edited = await conv.get_edit()
            assert edited.text == "Finished"
            assert edited.id == original.id
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_get_edit_raises_when_no_edit() -> None:
    """get_edit() raises RuntimeError when the bot has not edited any message."""
    client = ServerlessTelegramClient(build_application=_build_edit_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            # This handler only sends a plain sendMessage, no edit
            await conv.send_message("/edit_with_buttons")
            await conv.get_response()
            await conv.get_edit()  # consume the edit
            with pytest.raises(RuntimeError, match="No pending edit"):
                await conv.get_edit()  # second call should fail
    finally:
        await client.disconnect()
