from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING  # noqa: TID251

from telethon.tl.types import LabeledPrice

from tg_auto_test.test_utils.message_factory import build_serverless_message
from tg_auto_test.test_utils.message_factory_invoice import labeled_prices_from_call
from tg_auto_test.test_utils.models import FileData, ServerlessMessage, TelegramApiCall

if TYPE_CHECKING:
    from tg_auto_test.test_utils.poll_vote_handler import PollTracker

_MESSAGE_METHODS = frozenset({
    "sendMessage",
    "sendDocument",
    "sendVoice",
    "sendPhoto",
    "sendVideoNote",
    "sendInvoice",
    "sendPoll",
    "editMessageText",
})


def extract_responses(
    calls: list[TelegramApiCall],
    file_store: dict[str, FileData],
    invoices: dict[int, dict[str, str | int | list[LabeledPrice]]],
    click_callback: Callable[[int, str], Awaitable[ServerlessMessage]],
    poll_tracker: "PollTracker | None" = None,  # noqa: F821
) -> list[ServerlessMessage]:
    responses: list[ServerlessMessage] = []
    for call in calls:
        if call.api_method not in _MESSAGE_METHODS:
            continue
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
        elif call.api_method == "sendPoll" and poll_tracker is not None and message.poll_data is not None:
            # Track poll by message_id for SendVoteRequest handling
            if isinstance(message.poll_data, dict):
                poll_id = str(message.poll_data.get("id", ""))
                options = message.poll_data.get("options", [])
                if isinstance(options, list):
                    # Convert to proper format for poll tracker
                    options_data = [{"text": str(opt.get("text", ""))} for opt in options if isinstance(opt, dict)]
                    poll_tracker.track_poll(message.id, poll_id, options_data)
        responses.append(message)
    return responses
