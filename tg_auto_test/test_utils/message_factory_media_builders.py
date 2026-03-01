"""Builder functions that convert Telegram Bot API media calls into ServerlessMessage objects."""

from collections.abc import Callable

from telethon.tl.types import (
    DocumentAttributeAudio,
    DocumentAttributeFilename,
    DocumentAttributeVideo,
    Photo,
    PhotoSize,
    TypeDocumentAttribute,
)

from tg_auto_test.test_utils.media_metadata import audio_duration_seconds, mp4_duration_and_dimensions
from tg_auto_test.test_utils.message_factory_media import image_dimensions, make_document
from tg_auto_test.test_utils.models import FileData, ServerlessMessage

MediaBuilder = Callable[[str, bytes, FileData, dict[str, FileData]], ServerlessMessage]


def build_photo_message(
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
        _media_photo=photo,
        _raw_bytes=raw_bytes,
        _file_store=file_store,
        _response_file_id=file_id,
    )


def build_document_message(
    file_id: str,
    raw_bytes: bytes,
    file_data: FileData,
    file_store: dict[str, FileData],
) -> ServerlessMessage:
    attributes: list[TypeDocumentAttribute] = [DocumentAttributeFilename(file_name=file_data.filename)]
    doc = make_document(file_id, len(raw_bytes), file_data.content_type, attributes)
    return ServerlessMessage(
        _media_document=doc,
        _raw_bytes=raw_bytes,
        _file_store=file_store,
        _response_file_id=file_id,
    )


def build_voice_message(
    file_id: str,
    raw_bytes: bytes,
    file_data: FileData,
    file_store: dict[str, FileData],
) -> ServerlessMessage:
    duration_seconds = audio_duration_seconds(raw_bytes)
    if duration_seconds is None:
        raise RuntimeError(f"Failed to extract audio duration for {file_id}")
    duration = max(1, int(round(duration_seconds)))
    attributes: list[TypeDocumentAttribute] = [DocumentAttributeAudio(duration=duration, voice=True)]
    doc = make_document(file_id, len(raw_bytes), file_data.content_type, attributes)
    return ServerlessMessage(
        _media_document=doc,
        _raw_bytes=raw_bytes,
        _file_store=file_store,
        _response_file_id=file_id,
    )


def build_video_note_message(
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
    attributes: list[TypeDocumentAttribute] = [
        DocumentAttributeVideo(duration=duration, w=width, h=height, round_message=True),
    ]
    doc = make_document(file_id, len(raw_bytes), file_data.content_type, attributes)
    return ServerlessMessage(
        _media_document=doc,
        _raw_bytes=raw_bytes,
        _file_store=file_store,
        _response_file_id=file_id,
    )


def _build_video_like_message(
    file_id: str,
    raw_bytes: bytes,
    file_data: FileData,
    file_store: dict[str, FileData],
) -> ServerlessMessage:
    duration_seconds, width, height = mp4_duration_and_dimensions(raw_bytes)
    duration = max(1, int(round(duration_seconds))) if duration_seconds else 0
    attributes: list[TypeDocumentAttribute] = [
        DocumentAttributeVideo(duration=duration, w=width or 0, h=height or 0, round_message=False),
    ]
    doc = make_document(file_id, len(raw_bytes), file_data.content_type, attributes)
    return ServerlessMessage(
        _media_document=doc,
        _raw_bytes=raw_bytes,
        _file_store=file_store,
        _response_file_id=file_id,
    )


def build_audio_message(
    file_id: str,
    raw_bytes: bytes,
    file_data: FileData,
    file_store: dict[str, FileData],
) -> ServerlessMessage:
    duration_seconds = audio_duration_seconds(raw_bytes)
    duration = max(1, int(round(duration_seconds))) if duration_seconds else 0
    attributes: list[TypeDocumentAttribute] = [DocumentAttributeAudio(duration=duration, voice=False)]
    doc = make_document(file_id, len(raw_bytes), file_data.content_type, attributes)
    return ServerlessMessage(
        _media_document=doc,
        _raw_bytes=raw_bytes,
        _file_store=file_store,
        _response_file_id=file_id,
    )


MEDIA_METHOD_BUILDERS: dict[str, MediaBuilder] = {
    "sendPhoto": build_photo_message,
    "sendDocument": build_document_message,
    "sendVoice": build_voice_message,
    "sendVideoNote": build_video_note_message,
    "sendVideo": _build_video_like_message,
    "sendAnimation": _build_video_like_message,
    "sendAudio": build_audio_message,
    "sendSticker": build_document_message,
}
