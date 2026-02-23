import json

from telethon.tl.types import LabeledPrice, MessageMediaInvoice

from tg_auto_test.test_utils.models import ServerlessMessage, TelegramApiCall


def message_id_from_result(call: TelegramApiCall) -> int:
    if not isinstance(call.result, dict):
        raise RuntimeError(f"Expected dict result from {call.api_method}, got {type(call.result).__name__}")
    message_id = call.result.get("message_id")
    if message_id is None:
        raise RuntimeError(f"Missing 'message_id' in {call.api_method} result: {call.result}")
    if not isinstance(message_id, int | str):
        raise RuntimeError(f"Invalid 'message_id' type in {call.api_method} result: {type(message_id).__name__}")
    return int(message_id)


def labeled_prices_from_call(call: TelegramApiCall) -> list[LabeledPrice]:
    prices_raw = call.parameters["prices"]
    decoded = json.loads(prices_raw)
    if not isinstance(decoded, list):
        raise ValueError("Expected `prices` to decode into a list.")

    prices: list[LabeledPrice] = []
    for item in decoded:
        if not isinstance(item, dict):
            raise ValueError("Each price item must be an object.")
        label = item.get("label")
        amount = item.get("amount")
        if not isinstance(label, str):
            raise ValueError("Price label must be a string.")
        if not isinstance(amount, int | float | str):
            raise ValueError("Price amount must be numeric.")
        prices.append(LabeledPrice(label=label, amount=int(amount)))
    return prices


def build_invoice_message(call: TelegramApiCall) -> ServerlessMessage:
    prices = labeled_prices_from_call(call)
    total_amount = sum(price.amount for price in prices)
    invoice = MessageMediaInvoice(
        title=str(call.parameters.get("title", "")),
        description=str(call.parameters.get("description", "")),
        currency=str(call.parameters["currency"]),
        total_amount=total_amount,
        start_param=str(call.parameters.get("start_parameter", "")),
    )
    return ServerlessMessage(id=message_id_from_result(call), invoice_data=invoice)
