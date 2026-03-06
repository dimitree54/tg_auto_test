"""Reproduce GitHub issue #21: edit_text and delete_message bugs.

Bug 1 — edit_text appended as new outbox entry instead of replacing original:
    A handler that sends a message then edits it (reply_text + edit_text) produces
    two separate outbox entries.  conv.get_response() returns the original
    "Loading..." text instead of the edited "Done!" text.

    Root cause: ServerlessUpdateProcessor.process_message_update() appends ALL
    bot API responses to the outbox — both sendMessage and editMessageText —
    as separate entries.  The editMessageText response has _is_edit=True but the
    outbox never collapses edits onto the original message.

Bug 2 — delete_message has no handler at the Bot API layer:
    A handler that sends a message then deletes it triggers
    Bot.delete_message() → StubTelegramRequest.do_request("deleteMessage", …).
    Since "deleteMessage" is not in StubTelegramRequest._handlers, it raises
    AssertionError("Unexpected Telegram API method: deleteMessage").
"""

import pytest
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient

# ── handlers ──────────────────────────────────────────────────────────


async def _edit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message then immediately edit it."""
    del context
    if update.message:
        msg = await update.message.reply_text("Loading...")
        await msg.edit_text("Done!")


async def _delete_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a temporary status message, delete it, then send the real reply."""
    del context
    if update.message:
        tmp = await update.message.reply_text("Temporary status")
        await tmp.delete()
        await update.message.reply_text("Final result")


# ── application builders ──────────────────────────────────────────────


def _build_edit_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(CommandHandler("edit", _edit_handler))
    return app


def _build_delete_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(CommandHandler("delete", _delete_handler))
    return app


# ── Bug 1: edit_text produces wrong get_response() text ──────────────


@pytest.mark.asyncio
async def test_edit_text_get_response_returns_original() -> None:
    """conv.get_response() returns the original sendMessage, and get_edit() returns the edit.

    Matches real Telethon behavior: get_response() waits for sendMessage events,
    get_edit() waits for editMessageText events — they are separate queues.
    """
    client = ServerlessTelegramClient(build_application=_build_edit_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/edit")
            msg = await conv.get_response()
            assert msg.text == "Loading..."
            edited = await conv.get_edit()
            assert edited.text == "Done!"
            assert edited.id == msg.id
    finally:
        await client.disconnect()


# ── Bug 2: delete_message raises AssertionError ──────────────────────


@pytest.mark.asyncio
async def test_delete_message_does_not_crash() -> None:
    """msg.delete() must not raise AssertionError.

    Currently fails: StubTelegramRequest._handlers has no entry for
    "deleteMessage", so do_request raises
    AssertionError("Unexpected Telegram API method: deleteMessage").
    """
    client = ServerlessTelegramClient(build_application=_build_delete_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/delete")
            msg = await conv.get_response()
            assert msg.text == "Final result"
    finally:
        await client.disconnect()
