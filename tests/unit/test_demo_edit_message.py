"""Reproduce GitHub issue #19: Demo UI does not support bot message editing.

When a PTB bot calls ``query.message.edit_text()`` in a callback handler,
the Demo UI should update the existing message in-place. Instead, the
current implementation:
- Returns a new message_id (``_base_message`` always increments the counter)
  instead of preserving the original message's ID
- Has no ``is_edit`` field in ``MessageResponse`` to distinguish edits
  from new messages
- The frontend always appends a new bubble instead of updating in-place

These tests demonstrate the bug by building a PTB app whose callback
handler calls ``edit_message_text`` and verifying the Demo UI API
response reflects an edit rather than a brand-new message.
"""

from typing import cast

from fastapi.testclient import TestClient
import pytest
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from tests.unit.sse_helpers import parse_sse_messages
from tg_auto_test.demo_ui.server.demo_server import DemoClientProtocol, DemoServer
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


async def _menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send inline keyboard that the callback handler will edit."""
    del context
    if update.message:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Edit me", callback_data="do_edit")],
        ])
        await update.message.reply_text("Original text", reply_markup=keyboard)


async def _edit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Edit the original message text instead of sending a new message."""
    del context
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.message:
            await query.message.edit_text("Edited text")


def _build_edit_app(builder: ApplicationBuilder) -> Application:
    """Build a PTB app whose callback handler uses edit_message_text."""
    app = builder.build()
    app.add_handler(CommandHandler("menu", _menu_handler))
    app.add_handler(CallbackQueryHandler(_edit_callback))
    return app


@pytest.mark.asyncio
async def test_edit_message_preserves_message_id() -> None:
    """The edited message must keep the same message_id as the original.

    Currently fails because ``_base_message`` in ``stub_request_commands.py``
    always generates a new auto-incremented ID for ``editMessageText``,
    discarding the original ``message_id`` parameter.
    """
    client = ServerlessTelegramClient(build_application=_build_edit_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/menu")
            original = await conv.get_response()
            original_id = original.id

            edited = await original.click(data=b"do_edit")

            assert edited.text == "Edited text"
            msg = (
                f"editMessageText must preserve the original message_id ({original_id}), but got a new id ({edited.id})"
            )
            assert edited.id == original_id, msg
    finally:
        await client.disconnect()


def test_demo_api_callback_edit_returns_edit_flag() -> None:
    """The /api/callback response must include an is_edit flag.

    Currently fails because ``MessageResponse`` has no ``is_edit`` field
    and the Demo UI frontend has no way to distinguish edit responses
    from new messages.
    """
    client = ServerlessTelegramClient(build_application=_build_edit_app)
    server = DemoServer(cast(DemoClientProtocol, client), "test_bot")
    app = server.create_app()

    with TestClient(app) as http:
        # Step 1: send /menu to get inline keyboard
        resp = http.post("/api/message", json={"text": "/menu"})
        assert resp.status_code == 200
        messages = parse_sse_messages(resp)
        assert len(messages) >= 1
        menu_data = messages[0]
        assert menu_data["text"] == "Original text"
        original_msg_id = menu_data["message_id"]
        assert original_msg_id > 0

        # Step 2: click the inline button (triggers editMessageText)
        resp = http.post(
            "/api/callback",
            json={"message_id": original_msg_id, "data": "do_edit"},
        )
        assert resp.status_code == 200
        edit_data = resp.json()
        assert edit_data["text"] == "Edited text"

        # BUG: the response should indicate this is an edit and preserve
        # the original message_id, but currently it does neither.
        assert "is_edit" in edit_data, (
            "MessageResponse must include an 'is_edit' field so the "
            "frontend can update the message in-place instead of "
            "appending a new bubble"
        )
        assert edit_data["is_edit"] is True

        assert edit_data["message_id"] == original_msg_id, (
            f"editMessageText response must carry the original message_id "
            f"({original_msg_id}), but got {edit_data['message_id']}"
        )
