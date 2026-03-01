import json

from tg_auto_test.test_utils.entity_converter import convert_entities
from tg_auto_test.test_utils.media_types import MEDIA_PARAM_KEY
from tg_auto_test.test_utils.message_factory_invoice import build_invoice_message, message_id_from_result
from tg_auto_test.test_utils.message_factory_media_builders import MEDIA_METHOD_BUILDERS
from tg_auto_test.test_utils.message_factory_poll import build_poll_message
from tg_auto_test.test_utils.models import FileData, ReplyMarkup, ServerlessMessage, TelegramApiCall


def build_serverless_message(
    call: TelegramApiCall,
    file_store: dict[str, FileData],
) -> ServerlessMessage:
    message_id = message_id_from_result(call)
    if call.api_method in ("sendMessage", "editMessageText"):
        return _build_text_message(call, message_id)
    if call.api_method == "sendInvoice":
        return build_invoice_message(call)
    if call.api_method == "sendPoll":
        return build_poll_message(call)

    param_key = MEDIA_PARAM_KEY.get(call.api_method)
    if param_key is None:
        raise ValueError(f"Unsupported API method: {call.api_method}")

    file_id = call.parameters[param_key]
    raw_bytes, file_data = _resolve_file_data(call, file_id, file_store)

    builder = MEDIA_METHOD_BUILDERS.get(call.api_method)
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


def _extract_entities_from_result(call: TelegramApiCall) -> list[object]:
    """Extract and convert entities from the API response."""
    if not isinstance(call.result, dict):
        return []
    raw_entities = call.result.get("entities")
    if not isinstance(raw_entities, list):
        return []
    return convert_entities(raw_entities)


def _build_text_message(call: TelegramApiCall, message_id: int) -> ServerlessMessage:
    markup = _parse_reply_markup(call.parameters)
    text = _text_from_result(call)
    entities = _extract_entities_from_result(call)
    return ServerlessMessage(
        id=message_id,
        text=text,
        entities=entities,
        _reply_markup_data=markup,
    )


def _text_from_result(call: TelegramApiCall) -> str:
    """Get the processed text from the API response (HTML-stripped when applicable)."""
    if isinstance(call.result, dict):
        result_text = call.result.get("text")
        if isinstance(result_text, str):
            return result_text
    return call.parameters.get("text", "")
