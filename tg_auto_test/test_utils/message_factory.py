import json

from telethon.tl.types import (
    DocumentAttributeAudio,
    DocumentAttributeFilename,
    DocumentAttributeVideo,
    Photo,
    PhotoSize,
    TypeDocumentAttribute,
)

from tg_auto_test.test_utils.media_metadata import audio_duration_seconds, mp4_duration_and_dimensions
from tg_auto_test.test_utils.message_factory_invoice import build_invoice_message, message_id_from_result
from tg_auto_test.test_utils.message_factory_media import image_dimensions, make_document
from tg_auto_test.test_utils.models import FileData, ReplyMarkup, ServerlessMessage, TelegramApiCall

_MEDIA_PARAM_KEY: dict[str, str] = {
    "sendDocument": "document",
    "sendVoice": "voice",
    "sendPhoto": "photo",
    "sendVideoNote": "video_note",
}


def build_serverless_message(
    call: TelegramApiCall,
    file_store: dict[str, FileData],
) -> ServerlessMessage:
    message_id = message_id_from_result(call)
    if call.api_method in ("sendMessage", "editMessageText"):
        return _build_text_message(call, message_id)
    if call.api_method == "sendInvoice":
        return build_invoice_message(call)

    param_key = _MEDIA_PARAM_KEY.get(call.api_method)
    if param_key is None:
        raise ValueError(f"Unsupported API method: {call.api_method}")

    file_id = call.parameters[param_key]
    raw_bytes, file_data = _resolve_file_data(call, file_id, file_store)

    builder = _METHOD_BUILDERS.get(call.api_method)
    if builder is None:
        raise ValueError(f"No builder for API method: {call.api_method}")

    message = builder(file_id, raw_bytes, file_data, file_store)
    message.id = message_id
    return message


def _resolve_file_data(
    call: TelegramApiCall,
    file_id: str,
    file_store: dict[str, FileData],
) -> tuple[bytes, FileData]:
    if call.file is not None:
        return call.file.data, call.file
    store_entry = file_store.get(file_id)
    if store_entry is not None:
        return store_entry.data, store_entry
    raise RuntimeError(f"No file data for file_id={file_id} in {call.api_method}")


def _build_photo_message(
    file_id: str,
    raw_bytes: bytes,
    _file_data: FileData,
    file_store: dict[str, FileData],
) -> ServerlessMessage:
    width, height = image_dimensions(raw_bytes)
    photo = Photo(
        id=hash(file_id) & 0x7FFFFFFFFFFFFFFF,
        access_hash=0,
        file_reference=b"",
        date=None,
        dc_id=1,
        sizes=[PhotoSize(type="x", w=width, h=height, size=len(raw_bytes))],
    )
    return ServerlessMessage(
        media_photo=photo,
        raw_bytes=raw_bytes,
        file_store=file_store,
        response_file_id=file_id,
    )


def _build_document_message(
    file_id: str,
    raw_bytes: bytes,
    file_data: FileData,
    file_store: dict[str, FileData],
) -> ServerlessMessage:
    attributes: list[TypeDocumentAttribute] = []
    attributes.append(DocumentAttributeFilename(file_name=file_data.filename))
    doc = make_document(file_id, len(raw_bytes), file_data.content_type, attributes)
    return ServerlessMessage(
        media_document=doc,
        raw_bytes=raw_bytes,
        file_store=file_store,
        response_file_id=file_id,
    )


def _build_voice_message(
    file_id: str,
    raw_bytes: bytes,
    file_data: FileData,
    file_store: dict[str, FileData],
) -> ServerlessMessage:
    duration_seconds = audio_duration_seconds(raw_bytes)
    if duration_seconds is None:
        raise RuntimeError(f"Failed to extract audio duration for {file_id}")
    duration = max(1, int(round(duration_seconds)))
    attributes: list[TypeDocumentAttribute] = []
    attributes.append(DocumentAttributeAudio(duration=duration, voice=True))
    doc = make_document(file_id, len(raw_bytes), file_data.content_type, attributes)
    return ServerlessMessage(
        media_document=doc,
        raw_bytes=raw_bytes,
        file_store=file_store,
        response_file_id=file_id,
    )


def _build_video_note_message(
    file_id: str,
    raw_bytes: bytes,
    file_data: FileData,
    file_store: dict[str, FileData],
) -> ServerlessMessage:
    duration_seconds, width, height = mp4_duration_and_dimensions(raw_bytes)
    if duration_seconds is None:
        raise RuntimeError(f"Failed to extract video duration for {file_id}")
    if width is None or height is None:
        raise RuntimeError(f"Failed to extract video dimensions for {file_id}")
    duration = max(1, int(round(duration_seconds)))
    attributes: list[TypeDocumentAttribute] = []
    attributes.append(DocumentAttributeVideo(duration=duration, w=width, h=height, round_message=True))
    doc = make_document(file_id, len(raw_bytes), file_data.content_type, attributes)
    return ServerlessMessage(
        media_document=doc,
        raw_bytes=raw_bytes,
        file_store=file_store,
        response_file_id=file_id,
    )


def _parse_reply_markup(parameters: dict[str, str]) -> ReplyMarkup | None:
    raw = parameters.get("reply_markup")
    if raw is None:
        return None
    parsed_obj = json.loads(raw)
    if not isinstance(parsed_obj, dict):
        raise ValueError("reply_markup must decode to a JSON object")
    markup: ReplyMarkup = {}
    for key, value in parsed_obj.items():
        if not isinstance(key, str):
            raise ValueError("reply_markup keys must be strings")
        markup[key] = value
    return markup


def _build_text_message(call: TelegramApiCall, message_id: int) -> ServerlessMessage:
    markup = _parse_reply_markup(call.parameters)
    return ServerlessMessage(
        id=message_id,
        text=call.parameters.get("text", ""),
        reply_markup_data=markup,
    )


_METHOD_BUILDERS = {
    "sendPhoto": _build_photo_message,
    "sendDocument": _build_document_message,
    "sendVoice": _build_voice_message,
    "sendVideoNote": _build_video_note_message,
}
