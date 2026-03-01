"""Reproduce GitHub issue #18: Demo UI photo upload fails with unrecognized response.

When a bot responds to a photo upload with a media type not handled by the
stub request (e.g. sendVideo, sendAnimation, sendAudio, sendSticker), the
StubTelegramRequest raises AssertionError for the unknown API method. PTB
swallows this as a NetworkError, so no successful API call is recorded.
ServerlessUpdateProcessor.process_message_update then finds no recognizable
responses and raises RuntimeError("Bot did not send a recognizable response.").
"""

from io import BytesIO

from PIL import Image
import pytest
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters

from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


def _create_test_png() -> bytes:
    img = Image.new("RGB", (2, 2), color="red")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


async def _photo_reply_video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Bot handler that responds to a photo by sending a video back."""
    if update.message and update.message.photo:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        raw = await file.download_as_bytearray()
        await update.message.reply_video(bytes(raw))


def _build_video_reply_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(MessageHandler(filters.PHOTO, _photo_reply_video_handler))
    return app


@pytest.mark.asyncio
async def test_photo_upload_bot_replies_video() -> None:
    """Sending a photo to a bot that replies with sendVideo should succeed.

    This reproduces issue #18: the stub request does not handle sendVideo,
    so the bot's response is lost and process_message_update raises
    RuntimeError("Bot did not send a recognizable response.") instead of
    returning the video message.
    """
    client = ServerlessTelegramClient(build_application=_build_video_reply_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_file(_create_test_png())
            response = await conv.get_response()
            assert response is not None
    finally:
        await client.disconnect()
