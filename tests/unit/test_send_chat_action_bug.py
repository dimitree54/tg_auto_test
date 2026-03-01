"""Test reproducing GitHub issue #20: sendChatAction crashes the bot.

Many PTB bots call ``send_chat_action(ChatAction.TYPING)`` before long-running
operations.  The stub infrastructure does not include a handler for
``sendChatAction`` in ``_handlers``, so the call raises an ``AssertionError``
instead of succeeding silently.

This test creates a minimal bot handler that sends a typing indicator before
replying and verifies that the full round-trip works.
"""

import pytest
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


async def _typing_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Simulate a slow handler that sends a typing indicator first."""
    if update.message:
        await context.bot.send_chat_action(
            chat_id=update.message.chat_id,
            action=ChatAction.TYPING,
        )
        await update.message.reply_text("Done thinking!")


def _build_typing_app(builder: ApplicationBuilder) -> Application:
    """Build a PTB application with a handler that uses send_chat_action."""
    app = builder.build()
    app.add_handler(CommandHandler("think", _typing_handler))
    return app


@pytest.mark.asyncio
async def test_send_chat_action_does_not_crash() -> None:
    """A bot calling send_chat_action should not crash.

    Reproduces GitHub issue #20: ``sendChatAction`` is missing from the
    ``_handlers`` dict in ``stub_request.py``, causing an ``AssertionError``
    when the bot sends a typing indicator.
    """
    client = ServerlessTelegramClient(build_application=_build_typing_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/think")
            msg = await conv.get_response()
            assert msg.text == "Done thinking!"
    finally:
        await client.disconnect()
