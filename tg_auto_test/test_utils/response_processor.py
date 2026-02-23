from collections.abc import Awaitable, Callable

from telethon.tl.types import LabeledPrice

from tg_auto_test.test_utils.message_factory import build_serverless_message
from tg_auto_test.test_utils.message_factory_invoice import labeled_prices_from_call
from tg_auto_test.test_utils.models import FileData, ServerlessMessage, TelegramApiCall

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
        responses.append(message)
    return responses
