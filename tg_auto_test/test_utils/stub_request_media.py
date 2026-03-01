import json
from typing import Protocol

from tg_auto_test.test_utils.html_parser import parse_html
from tg_auto_test.test_utils.json_types import JsonValue
from tg_auto_test.test_utils.media_metadata import audio_duration_seconds, mp4_duration_and_dimensions
from tg_auto_test.test_utils.media_types import MEDIA_PARAM_KEY
from tg_auto_test.test_utils.message_factory_media import image_dimensions
from tg_auto_test.test_utils.models import FileData, TelegramApiCall


class _MediaHost(Protocol):
    calls: list[TelegramApiCall]
    file_store: dict[str, FileData]
    _next_poll_id: int

    def _base_message(self, parameters: dict[str, str]) -> dict[str, JsonValue]: ...

    def _ok_response(self, result: JsonValue) -> tuple[int, bytes]: ...


class MediaMixin:
    def _handle_send_invoice(self: _MediaHost, parameters: dict[str, str]) -> tuple[int, bytes]:
        msg: dict[str, JsonValue] = self._base_message(parameters)
        prices = parameters["prices"]
        total_amount = 0
        for item in json.loads(prices):
            if not isinstance(item, dict):
                raise ValueError("Each invoice price item must be an object.")
            amount = item.get("amount")
            if not isinstance(amount, int | float | str):
                raise ValueError("Invoice price amount must be numeric.")
            total_amount += int(amount)
        invoice: dict[str, JsonValue] = {
            "title": parameters["title"],
            "description": parameters["description"],
            "start_parameter": parameters["start_parameter"],
            "currency": parameters["currency"],
            "total_amount": total_amount,
        }
        msg["invoice"] = invoice
        return self._ok_response(msg)

    def _handle_send_media(self: _MediaHost, parameters: dict[str, str]) -> tuple[int, bytes]:
        msg: dict[str, JsonValue] = self._base_message(parameters)
        call = self.calls[-1]
        method = call.api_method
        fid = parameters[MEDIA_PARAM_KEY[method]]
        raw = _resolve_bytes(call, fid, self.file_store)
        base: dict[str, JsonValue] = {"file_id": fid, "file_unique_id": f"unique_{fid}"}

        if method == "sendDocument":
            msg["document"] = base
        elif method == "sendVoice":
            dur = audio_duration_seconds(raw)
            if dur is None:
                raise RuntimeError("Cannot determine audio duration for voice message")
            base["duration"] = max(1, int(round(dur)))
            msg["voice"] = base
        elif method == "sendPhoto":
            w, h = image_dimensions(raw)
            photo_item: dict[str, JsonValue] = {**base, "width": w, "height": h}
            photo: list[JsonValue] = [photo_item]
            msg["photo"] = photo
        elif method == "sendVideoNote":
            dur, w, _h = mp4_duration_and_dimensions(raw)
            if dur is None or w is None:
                raise RuntimeError("Cannot determine duration/dimensions for video note")
            base["length"] = w
            base["duration"] = max(1, int(round(dur)))
            msg["video_note"] = base
        elif method in ("sendVideo", "sendAnimation"):
            dur, w, h = mp4_duration_and_dimensions(raw)
            base["duration"] = max(1, int(round(dur))) if dur is not None else 0
            base["width"] = w if w is not None else 0
            base["height"] = h if h is not None else 0
            msg["video" if method == "sendVideo" else "animation"] = base
        elif method == "sendAudio":
            dur = audio_duration_seconds(raw)
            base["duration"] = max(1, int(round(dur))) if dur is not None else 0
            msg["audio"] = base
        elif method == "sendSticker":
            msg["sticker"] = base

        caption = parameters.get("caption", "")
        parse_mode = parameters.get("parse_mode", "")
        if caption and parse_mode.lower() == "html":
            parsed_caption, caption_entities = parse_html(caption)
            msg["caption"] = parsed_caption
            if caption_entities:
                msg["caption_entities"] = caption_entities
        elif caption:
            msg["caption"] = caption

        return self._ok_response(msg)

    def _handle_send_poll(self: _MediaHost, parameters: dict[str, str]) -> tuple[int, bytes]:
        msg: dict[str, JsonValue] = self._base_message(parameters)

        poll_id = f"poll_{self._next_poll_id}"
        self._next_poll_id += 1

        options_json = parameters["options"]
        options_list = json.loads(options_json)

        # Options can be either list of strings or list of InputPollOption objects
        if not isinstance(options_list, list):
            raise ValueError("Poll options must be a list")

        poll_options = []
        for i, option in enumerate(options_list):
            if isinstance(option, str):
                poll_options.append({"text": option, "voter_count": 0})
            elif isinstance(option, dict) and "text" in option:
                poll_options.append({"text": option["text"], "voter_count": 0})
            else:
                raise ValueError("Poll options must be strings or objects with 'text' field")

        poll: dict[str, JsonValue] = {
            "id": poll_id,
            "question": parameters["question"],
            "options": poll_options,
            "total_voter_count": 0,
            "is_closed": False,
            "is_anonymous": parameters.get("is_anonymous", "true") == "true",
            "type": parameters.get("type", "regular"),
            "allows_multiple_answers": False,
        }
        msg["poll"] = poll
        return self._ok_response(msg)


def _resolve_bytes(call: TelegramApiCall, file_id: str, file_store: dict[str, FileData]) -> bytes:
    if call.file is not None:
        return call.file.data
    entry = file_store.get(file_id)
    if entry is None:
        raise RuntimeError(f"No file data for file_id={file_id!r}: not uploaded and not in file store")
    return entry.data
