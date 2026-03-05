"""Reproduce GitHub issue #23: Demo UI does not show intermediate bot messages.

The POST /api/message endpoint uses SSE (Server-Sent Events) so each
response is flushed to the client as the handler produces it.
"""

from typing import cast

from fastapi.testclient import TestClient
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters

from tests.unit.sse_helpers import parse_sse_messages
from tg_auto_test.demo_ui.server.demo_server import DemoClientProtocol, DemoServer
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


async def _single_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.message:
        return
    await update.message.reply_text("hi")


def _build_single_reply_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _single_reply_handler))
    return app


async def _two_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.message:
        return
    await update.message.reply_text("first")
    await update.message.reply_text("second")


def _build_two_reply_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _two_reply_handler))
    return app


def test_message_endpoint_uses_sse_content_type() -> None:
    """POST /api/message must return content-type text/event-stream."""
    real_client = ServerlessTelegramClient(_build_single_reply_app)

    server = DemoServer(cast(DemoClientProtocol, real_client), "test_bot")
    app = server.create_app()

    with TestClient(app) as client:
        resp = client.post("/api/message", json={"text": "hello"})

    assert resp.status_code == 200
    content_type = resp.headers.get("content-type", "")
    assert "text/event-stream" in content_type


def test_sse_events_contain_all_messages() -> None:
    """The SSE stream must contain every bot response plus a [DONE] sentinel."""
    real_client = ServerlessTelegramClient(_build_two_reply_app)

    server = DemoServer(cast(DemoClientProtocol, real_client), "test_bot")
    app = server.create_app()

    with TestClient(app) as client:
        resp = client.post("/api/message", json={"text": "go"})

    messages = parse_sse_messages(resp)
    assert len(messages) == 2
    assert messages[0]["text"] == "first"
    assert messages[1]["text"] == "second"
    assert "data: [DONE]" in resp.text
