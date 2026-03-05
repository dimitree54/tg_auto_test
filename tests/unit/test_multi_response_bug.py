"""Reproduce GitHub issue #22: Demo server drops subsequent bot messages.

When a bot handler sends multiple messages (e.g. two reply_text calls),
all of them must be returned to the frontend via SSE.
"""

import io
from typing import cast

from fastapi.testclient import TestClient
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters

from tests.unit.sse_helpers import make_png_bytes, parse_sse_messages
from tg_auto_test.demo_ui.server.demo_server import DemoClientProtocol, DemoServer
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


async def _multi_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.message:
        return
    await update.message.reply_text("First response")
    await update.message.reply_text("Second response")


def _build_multi_text_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _multi_text_handler))
    return app


async def _multi_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.message:
        return
    await update.message.reply_text("Got your photo!")
    await update.message.reply_text("Processing complete.")


def _build_multi_photo_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(MessageHandler(filters.PHOTO, _multi_photo_handler))
    return app


async def _multi_document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.message:
        return
    await update.message.reply_text("Got your document!")
    await update.message.reply_text("Document processed.")


def _build_multi_document_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(MessageHandler(filters.Document.ALL, _multi_document_handler))
    return app


def test_message_endpoint_returns_all_bot_responses() -> None:
    """POST /api/message must return ALL bot responses, not just the first."""
    real_client = ServerlessTelegramClient(_build_multi_text_app)

    server = DemoServer(cast(DemoClientProtocol, real_client), "test_bot")
    app = server.create_app()

    with TestClient(app) as client:
        response = client.post("/api/message", json={"text": "hello"})

    assert response.status_code == 200
    messages = parse_sse_messages(response)
    assert len(messages) == 2
    assert messages[0]["text"] == "First response"
    assert messages[1]["text"] == "Second response"


def test_photo_endpoint_returns_all_bot_responses() -> None:
    """POST /api/photo must return ALL bot responses, not just the first."""
    real_client = ServerlessTelegramClient(_build_multi_photo_app)

    server = DemoServer(cast(DemoClientProtocol, real_client), "test_bot")
    app = server.create_app()

    with TestClient(app) as client:
        response = client.post(
            "/api/photo",
            files={"file": ("img.png", io.BytesIO(make_png_bytes()), "image/png")},
        )

    assert response.status_code == 200
    messages = parse_sse_messages(response)
    assert len(messages) == 2
    assert messages[0]["text"] == "Got your photo!"
    assert messages[1]["text"] == "Processing complete."


def test_document_endpoint_returns_all_bot_responses() -> None:
    """POST /api/document must return ALL bot responses, not just the first."""
    real_client = ServerlessTelegramClient(_build_multi_document_app)

    server = DemoServer(cast(DemoClientProtocol, real_client), "test_bot")
    app = server.create_app()

    with TestClient(app) as client:
        response = client.post(
            "/api/document",
            files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
        )

    assert response.status_code == 200
    messages = parse_sse_messages(response)
    assert len(messages) == 2
    assert messages[0]["text"] == "Got your document!"
    assert messages[1]["text"] == "Document processed."
