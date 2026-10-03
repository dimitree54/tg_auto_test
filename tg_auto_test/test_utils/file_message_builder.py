from pathlib import Path

from telethon.tl.types import TypeMessageEntity

from tg_auto_test.test_utils.incoming_text import apply_incoming_text
from tg_auto_test.test_utils.json_types import JsonValue
from tg_auto_test.test_utils.media_metadata import audio_duration_seconds, mp4_duration_and_dimensions
from tg_auto_test.test_utils.message_factory_media import image_dimensions


def build_file_payload(
    msg: dict[str, JsonValue],
    file_id: str,
    file: Path | bytes,
    *,
    file_bytes: bytes,
    caption: str,
    force_document: bool,
    voice_note: bool,
    video_note: bool,
    parse_mode: object = (),
    formatting_entities: list[TypeMessageEntity] | None = None,
) -> None:
    base: dict[str, JsonValue] = {"file_id": file_id, "file_unique_id": f"unique_{file_id}"}

    if video_note:
        dur, w, _h = mp4_duration_and_dimensions(file_bytes)
        if dur is None or w is None:
            raise RuntimeError(f"Failed to extract video note metadata from {len(file_bytes)} bytes")
        msg["video_note"] = {**base, "length": w, "duration": max(1, int(round(dur)))}
    elif voice_note:
        dur = audio_duration_seconds(file_bytes)
        if dur is None:
            raise RuntimeError(f"Failed to extract audio duration from {len(file_bytes)} bytes")
        msg["voice"] = {**base, "duration": max(1, int(round(dur)))}
    elif force_document:
        msg["document"] = {**base, "file_name": file.name if isinstance(file, Path) else "file"}
    else:
        w, h = image_dimensions(file_bytes)
        photo_item: dict[str, JsonValue] = {**base, "width": w, "height": h}
        photo: list[JsonValue] = [photo_item]
        msg["photo"] = photo

    if caption:
        apply_incoming_text(msg, caption, caption=True, parse_mode=parse_mode, formatting_entities=formatting_entities)
