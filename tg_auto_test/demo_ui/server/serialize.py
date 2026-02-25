"""Message serialization utilities for converting messages to API responses."""

import uuid

from tg_auto_test.demo_ui.server.api_models import MessageResponse
from tg_auto_test.demo_ui.server.file_store import FileStore


def _serialize_buttons(buttons: list[list[object]]) -> dict[str, list[list[dict[str, str]]]]:
    """Convert button objects to reply markup structure expected by frontend."""
    inline_keyboard = []
    for row in buttons:
        button_row = []
        for button in row:
            button_text = getattr(button, "text", "")
            button_data = getattr(button, "data", b"")
            if isinstance(button_data, bytes):
                button_data = button_data.decode("utf-8", errors="ignore")
            button_row.append({"text": str(button_text), "callback_data": str(button_data)})
        inline_keyboard.append(button_row)
    return {"inline_keyboard": inline_keyboard}


async def serialize_message(message: object, file_store: FileStore) -> MessageResponse:
    """Convert a message to MessageResponse for the API."""
    # Handle poll messages via Telethon-standard .poll property
    poll = getattr(message, "poll", None)
    if poll is not None:
        # Use Telethon MessageMediaPoll structure
        poll_data = getattr(poll, "poll", None)
        question = ""
        poll_id = ""

        if poll_data:
            # Handle TextWithEntities or plain string
            question_obj = getattr(poll_data, "question", "")
            if hasattr(question_obj, "text"):
                question = str(question_obj.text)
            else:
                question = str(question_obj)
            poll_id = str(getattr(poll_data, "id", ""))

        options = []
        if poll_data:
            answers = getattr(poll_data, "answers", [])
            for answer in answers:
                answer_text_obj = getattr(answer, "text", "")
                # Handle TextWithEntities or plain string
                if hasattr(answer_text_obj, "text"):
                    answer_text = str(answer_text_obj.text)
                else:
                    answer_text = str(answer_text_obj)
                options.append({"text": answer_text, "voter_count": 0})

        return MessageResponse(
            type="poll",
            message_id=getattr(message, "id", 0),
            poll_question=question,
            poll_options=options,
            poll_id=poll_id,
        )

    # Handle invoice messages
    invoice = getattr(message, "invoice", None)
    if invoice is not None:
        return MessageResponse(
            type="invoice",
            message_id=getattr(message, "id", 0),
            title=getattr(invoice, "title", ""),
            description=getattr(invoice, "description", ""),
            currency=getattr(invoice, "currency", ""),
            total_amount=getattr(invoice, "total_amount", 0),
        )

    # Determine message type based on media (using Telethon-standard properties)
    msg_type = "text"
    file_id = ""
    filename = ""

    photo = getattr(message, "photo", None)
    document = getattr(message, "document", None)
    voice = getattr(message, "voice", None)
    video_note = getattr(message, "video_note", None)

    if photo:
        msg_type = "photo"
    elif document:
        msg_type = "document"
    elif voice:
        msg_type = "voice"
    elif video_note:
        msg_type = "video_note"

    # Handle file downloads and storage
    if msg_type != "text":
        # Use UUID instead of response_file_id (no more private fields)
        file_id = str(uuid.uuid4())

        # Try to download media using standard .download_media() method
        download_media = getattr(message, "download_media", None)
        if download_media:
            media_bytes = await download_media(file=bytes)
            if media_bytes is not None:
                # Get filename and content type from file properties
                file_obj = getattr(message, "file", None)
                if file_obj and getattr(file_obj, "name", None):
                    filename = file_obj.name
                else:
                    # Generate fallback filename based on type
                    extensions = {"photo": ".jpg", "document": "", "voice": ".ogg", "video_note": ".mp4"}
                    filename = f"{msg_type}{extensions.get(msg_type, '')}"

                content_type = "application/octet-stream"
                if file_obj and getattr(file_obj, "mime_type", None):
                    content_type = file_obj.mime_type
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

    # Convert reply markup using .buttons property
    reply_markup = None
    buttons = getattr(message, "buttons", None)
    if buttons:
        reply_markup = _serialize_buttons(buttons)

    return MessageResponse(
        type=msg_type,
        text=getattr(message, "text", ""),
        file_id=file_id,
        filename=filename,
        message_id=getattr(message, "id", 0),
        reply_markup=reply_markup,
    )


async def store_response_file(
    file_id: str,
    message: object,
    file_store: FileStore,
    fallback_filename: str,
    fallback_content_type: str,
    fallback_data: bytes,
) -> str:
    """Store file from bot response or use fallback data."""
    # Try to get media from bot response using standard .download_media() method
    download_media = getattr(message, "download_media", None)
    if download_media:
        bot_data = await download_media(file=bytes)
        if bot_data is not None:
            filename = fallback_filename
            content_type = fallback_content_type

            file_obj = getattr(message, "file", None)
            if file_obj:
                if getattr(file_obj, "name", None):
                    filename = file_obj.name
                if getattr(file_obj, "mime_type", None):
                    content_type = file_obj.mime_type

            file_store.store(file_id, filename, content_type, bot_data)
            return filename

    # Use fallback data if no media available
    file_store.store(file_id, fallback_filename, fallback_content_type, fallback_data)
    return fallback_filename
