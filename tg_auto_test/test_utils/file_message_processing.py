from pathlib import Path

from telethon.tl.types import TypeMessageEntity

from tg_auto_test.test_utils.file_message_builder import build_file_payload
from tg_auto_test.test_utils.json_types import JsonValue
from tg_auto_test.test_utils.media_types import detect_content_type
from tg_auto_test.test_utils.models import FileData


def process_file_message_data(
    file: Path | bytes,
    *,
    caption: str = "",  # noqa: ARG001
    force_document: bool = False,
    voice_note: bool = False,
    video_note: bool = False,
) -> tuple[bytes, str, str, FileData]:
    """Process file data and return components needed for message building."""
    file_bytes = file if isinstance(file, bytes) else file.read_bytes()
    fname = file.name if isinstance(file, Path) else "file"
    content_type = detect_content_type(fname, force_document, voice_note, video_note)
    file_data = FileData(data=file_bytes, filename=fname, content_type=content_type)
    return file_bytes, fname, content_type, file_data


def build_file_message_payload(
    payload: dict[str, JsonValue],  # noqa: ARG001
    msg: dict[str, JsonValue],
    file_id: str,
    file: Path | bytes,
    file_bytes: bytes,
    caption: str,
    force_document: bool,
    voice_note: bool,
    video_note: bool,
    *,
    parse_mode: object = (),
    formatting_entities: list[TypeMessageEntity] | None = None,
) -> None:
    """Build file message payload."""
    build_file_payload(
        msg,
        file_id,
        file,
        file_bytes=file_bytes,
        caption=caption,
        parse_mode=parse_mode,
        formatting_entities=formatting_entities,
        force_document=force_document,
        voice_note=voice_note,
        video_note=video_note,
    )


async def process_complete_file_message(
    client: object,
    file: Path | bytes,
    *,
    caption: str = "",
    parse_mode: object = (),
    formatting_entities: list[TypeMessageEntity] | None = None,
    force_document: bool = False,
    voice_note: bool = False,
    video_note: bool = False,
) -> object:
    """Complete file message processing for the client."""
    client._outbox.clear()  # noqa: SLF001
    client._edit_outbox.clear()  # noqa: SLF001
    file_id = client._helpers.make_file_id()  # noqa: SLF001
    file_bytes, fname, _ct, file_data = process_file_message_data(
        file, caption=caption, force_document=force_document, voice_note=voice_note, video_note=video_note
    )
    client._request.file_store[file_id] = file_data  # noqa: SLF001
    payload, msg = client._helpers.base_message_update(client._chat_id)  # noqa: SLF001
    build_file_message_payload(
        payload,
        msg,
        file_id,
        file,
        file_bytes,
        caption,
        force_document,
        voice_note,
        video_note,
        parse_mode=parse_mode,
        formatting_entities=formatting_entities,
    )
    return await client._process_message_update(payload)  # noqa: SLF001
