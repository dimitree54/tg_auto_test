"""Reproduce GitHub issue #24: get_edit() raises NotImplementedError.

The standard Telethon bot-testing pattern is:

    async with client.conversation(bot_username) as conv:
        await conv.send_message("hello")
        status = await conv.get_response()      # initial "Loading..." message
        result = await conv.get_edit()           # waits for editMessageText

ServerlessTelegramConversation.get_edit() unconditionally raises
NotImplementedError, even though the underlying outbox already handles
editMessageText via _replace_edited_message().  The plumbing is there
but get_edit() is never wired up to expose edited messages.
"""

import pytest
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


async def _status_then_edit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a status message, then edit it with the final result."""
    del context
    if update.message:
        status = await update.message.reply_text("Loading...")
        await status.edit_text("Done!")


def _build_status_edit_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(CommandHandler("work", _status_then_edit_handler))
    return app


@pytest.mark.asyncio
async def test_get_edit_no_longer_raises() -> None:
    """get_edit() must work after the fix for GitHub issue #24."""
    client = ServerlessTelegramClient(build_application=_build_status_edit_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/work")
            _status = await conv.get_response()
            edited = await conv.get_edit()
            assert edited.text == "Done!"
    finally:
        await client.disconnect()


class TestGetEditExpectedBehavior:
    """Verify the expected behavior once get_edit() is implemented."""

    @pytest.mark.asyncio
    async def test_get_edit_returns_edited_message(self) -> None:
        """After send→edit, get_edit() should return the edited message text."""
        client = ServerlessTelegramClient(build_application=_build_status_edit_app)
        await client.connect()
        try:
            async with client.conversation("test_bot") as conv:
                await conv.send_message("/work")
                status = await conv.get_response()
                assert status.text == "Done!", f"get_response() returned '{status.text}'"
                edited = await conv.get_edit()
                assert edited.text == "Done!", f"get_edit() returned '{edited.text}'"

        finally:
            await client.disconnect()

    @pytest.mark.asyncio
    async def test_get_edit_returns_same_message_id(self) -> None:
        """The edited message must preserve the original message_id."""
        client = ServerlessTelegramClient(build_application=_build_status_edit_app)
        await client.connect()
        try:
            async with client.conversation("test_bot") as conv:
                await conv.send_message("/work")
                status = await conv.get_response()
                edited = await conv.get_edit()
                assert edited.id == status.id, f"Edited id ({edited.id}) != original ({status.id})"
        finally:
            await client.disconnect()

    @pytest.mark.asyncio
    async def test_get_edit_preserves_reply_markup(self) -> None:
        """get_edit() should preserve reply_markup if the edit includes one."""

        async def _edit_with_buttons_handler(
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
        ) -> None:
            del context
            if not update.message:
                return
            status = await update.message.reply_text("Translating...")
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Option A", callback_data="a")],
            ])
            await status.edit_text("Translation complete!", reply_markup=keyboard)

        def _build_edit_with_buttons_app(builder: ApplicationBuilder) -> Application:
            app = builder.build()
            app.add_handler(CommandHandler("translate", _edit_with_buttons_handler))
            return app

        client = ServerlessTelegramClient(build_application=_build_edit_with_buttons_app)
        await client.connect()
        try:
            async with client.conversation("test_bot") as conv:
                await conv.send_message("/translate")
                _status = await conv.get_response()
                edited = await conv.get_edit()
                assert edited.text == "Translation complete!"
                assert edited.buttons is not None, "Edited message must include inline buttons"
        finally:
            await client.disconnect()
