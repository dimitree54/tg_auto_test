"""Reproduce bug: sending a photo to a bot with no photo handler gives HTTP 500.

When a bot does NOT handle photos (e.g., it only handles text messages), sending
a photo through the Demo UI returns "Upload error: POST /api/photo failed: 500
Internal Server Error" instead of a clear, user-friendly error message.

The root cause: ServerlessUpdateProcessor.process_message_update raises
RuntimeError("Bot did not send a recognizable response.") when the bot produces
no API calls in response to the photo. This propagates uncaught through the
FastAPI routes, resulting in an HTTP 500 instead of a meaningful error.

These tests assert the EXPECTED (correct) behavior, so they FAIL against the
current buggy code:
1. The /api/photo endpoint should return a 4xx (not 500) with a descriptive
   JSON error body.
2. At the client level, the error should NOT be a bare RuntimeError.
"""

import io
from typing import cast

from fastapi.testclient import TestClient
from PIL import Image
import pytest
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from tg_auto_test.demo_ui.server.demo_server import DemoClientProtocol, DemoServer
from tg_auto_test.test_utils.exceptions import BotNoResponseError
from tg_auto_test.test_utils.serverless_telegram_client import (
    ServerlessTelegramClient,
)


def _create_test_png() -> bytes:
    img = Image.new("RGB", (2, 2), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


async def _echo_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message and update.message.text:
        await update.message.reply_text(update.message.text)


def _build_text_only_app(builder: ApplicationBuilder) -> Application:
    """Build a PTB app that ONLY handles text messages -- no photo handler."""
    app = builder.build()
    app.add_handler(CommandHandler("start", _echo_text_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _echo_text_handler))
    return app


@pytest.mark.asyncio
async def test_photo_to_text_only_bot_gives_clear_error() -> None:
    """Sending a photo to a text-only bot should raise BotNoResponseError."""
    client = ServerlessTelegramClient(build_application=_build_text_only_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            with pytest.raises(BotNoResponseError, match="did not respond"):
                await conv.send_file(_create_test_png())
    finally:
        await client.disconnect()


def test_photo_endpoint_returns_proper_error_for_text_only_bot() -> None:
    """The /api/photo endpoint should return 4xx (not 500) with a clear message.

    Currently FAILS: the endpoint returns HTTP 500 because the RuntimeError
    propagates uncaught. The fix should catch this and return a proper
    HTTP 4xx response with a JSON body containing a user-friendly message.
    """
    client = ServerlessTelegramClient(build_application=_build_text_only_app)
    server = DemoServer(cast(DemoClientProtocol, client), "test_bot")
    app = server.create_app()

    png_bytes = _create_test_png()

    with TestClient(app, raise_server_exceptions=False) as http_client:
        response = http_client.post(
            "/api/photo",
            files={
                "file": ("test.png", io.BytesIO(png_bytes), "image/png"),
            },
        )

    # BUG: The server currently returns 500 Internal Server Error.
    # The expected behavior is a 4xx client error with a useful message.
    assert response.status_code != 500, (
        f"BUG: Got HTTP {response.status_code} Internal Server Error. "
        "The RuntimeError propagated uncaught through the route. "
        "Expected a 4xx response with a user-friendly error message."
    )
