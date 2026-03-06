from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING  # noqa: TID251

from telethon.tl.types import LabeledPrice

from tg_auto_test.test_utils.message_factory import build_serverless_message
from tg_auto_test.test_utils.message_factory_invoice import labeled_prices_from_call
from tg_auto_test.test_utils.models import FileData, ServerlessMessage, TelegramApiCall
from tg_auto_test.test_utils.serverless_bot_callback_answer import ServerlessBotCallbackAnswer

if TYPE_CHECKING:
    from tg_auto_test.test_utils.poll_vote_handler import PollTracker

_MESSAGE_METHODS = frozenset({
    "sendMessage",
    "sendDocument",
    "sendVoice",
    "sendPhoto",
    "sendVideoNote",
    "sendVideo",
    "sendAnimation",
    "sendAudio",
    "sendSticker",
    "sendInvoice",
    "sendPoll",
    "editMessageText",
})


def process_api_call(
    call: TelegramApiCall,
    file_store: dict[str, FileData],
    invoices: dict[int, dict[str, str | int | list[LabeledPrice]]],
    click_callback: Callable[[int, str], Awaitable[ServerlessBotCallbackAnswer]],
    poll_tracker: "PollTracker | None" = None,
) -> ServerlessMessage:
    """Build a ``ServerlessMessage`` from an API call and register side-effects."""
    message = build_serverless_message(call=call, file_store=file_store)
    message._click_callback = click_callback  # noqa: SLF001
    if call.api_method == "sendInvoice" and message.invoice is not None:
        prices = labeled_prices_from_call(call)
        invoices[message.id] = {
            "payload": call.parameters["payload"],
            "currency": message.invoice.currency,
            "prices": prices,
            "total_amount": sum(price.amount for price in prices),
        }
    elif call.api_method == "sendPoll" and poll_tracker is not None and message._poll_data is not None:  # noqa: SLF001
        _track_poll(poll_tracker, message)
    return message


def _track_poll(poll_tracker: "PollTracker", message: ServerlessMessage) -> None:
    if not isinstance(message._poll_data, dict):  # noqa: SLF001
        return
    poll_id = str(message._poll_data.get("id", ""))  # noqa: SLF001
    options = message._poll_data.get("options", [])
    if not isinstance(options, list):
        return
    options_data = [{"text": str(opt.get("text", ""))} for opt in options if isinstance(opt, dict)]
    poll_tracker.track_poll(message.id, poll_id, options_data)


def extract_responses(
    calls: list[TelegramApiCall],
    file_store: dict[str, FileData],
    invoices: dict[int, dict[str, str | int | list[LabeledPrice]]],
    click_callback: Callable[[int, str], Awaitable[ServerlessBotCallbackAnswer]],
    poll_tracker: "PollTracker | None" = None,
) -> list[ServerlessMessage]:
    responses: list[ServerlessMessage] = []
    for call in calls:
        if call.api_method not in _MESSAGE_METHODS:
            continue
        responses.append(process_api_call(call, file_store, invoices, click_callback, poll_tracker))
    return responses
