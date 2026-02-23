"""Message serialization utilities for converting messages to API responses."""

import uuid

from tg_auto_test.demo_ui.server.api_models import MessageResponse
from tg_auto_test.demo_ui.server.file_store import FileStore
from tg_auto_test.test_utils.models import ServerlessMessage


async def serialize_message(message: ServerlessMessage, file_store: FileStore) -> MessageResponse:
    """Convert a ServerlessMessage to MessageResponse for the API."""
    # Handle invoice messages
    if message.invoice is not None:
        invoice = message.invoice
        return MessageResponse(
            type="invoice",
            message_id=message.id,
            title=invoice.title,
            description=invoice.description,
            currency=invoice.currency,
            total_amount=invoice.total_amount,
        )

    # Determine message type based on media
    msg_type = "text"
    file_id = ""
    filename = ""

    if message.photo:
        msg_type = "photo"
    elif message.document:
        msg_type = "document"
    elif message.voice:
        msg_type = "voice"
    elif message.video_note:
        msg_type = "video_note"

    # Handle file downloads and storage
    if msg_type != "text":
        file_id = message.response_file_id or str(uuid.uuid4())

        # Try to download media
        media_bytes = await message.download_media(file=bytes)
        if media_bytes is not None:
            # Get filename and content type from file properties
            if message.file and message.file.name:
                filename = message.file.name
            else:
                # Generate fallback filename based on type
                extensions = {"photo": ".jpg", "document": "", "voice": ".ogg", "video_note": ".mp4"}
                filename = f"{msg_type}{extensions.get(msg_type, '')}"

            content_type = "application/octet-stream"
            if message.file and message.file.mime_type:
                content_type = message.file.mime_type
            else:
                # Generate fallback content type
                content_types = {
                    "photo": "image/jpeg",
                    "voice": "audio/ogg",
                    "video_note": "video/mp4",
                    "document": "application/octet-stream",
                }
                content_type = content_types.get(msg_type, "application/octet-stream")

            file_store.store(file_id, filename, content_type, media_bytes)

    # Convert reply markup
    reply_markup = None
    if message.reply_markup_data:
        reply_markup = message.reply_markup_data

    return MessageResponse(
        type=msg_type,
        text=message.text,
        file_id=file_id,
        filename=filename,
        message_id=message.id,
        reply_markup=reply_markup,
    )


async def store_response_file(
    file_id: str,
    message: ServerlessMessage,
    file_store: FileStore,
    fallback_filename: str,
    fallback_content_type: str,
    fallback_data: bytes,
) -> str:
    """Store file from bot response or use fallback data."""
    # Try to get media from bot response
    bot_data = await message.download_media(file=bytes)
    if bot_data is not None:
        filename = fallback_filename
        content_type = fallback_content_type

        if message.file:
            if message.file.name:
                filename = message.file.name
            if message.file.mime_type:
                content_type = message.file.mime_type

        file_store.store(file_id, filename, content_type, bot_data)
        return filename

    # Use fallback data if no media available
    file_store.store(file_id, fallback_filename, fallback_content_type, fallback_data)
    return fallback_filename
