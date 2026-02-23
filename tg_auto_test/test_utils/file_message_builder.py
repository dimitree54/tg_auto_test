from pathlib import Path

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
        msg["caption"] = caption
        if caption.startswith("/"):
            entity: dict[str, JsonValue] = {"offset": 0, "length": len(caption), "type": "bot_command"}
            entities: list[JsonValue] = [entity]
            msg["caption_entities"] = entities
