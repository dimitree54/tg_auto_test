"""Helpers for building serverless demo trace requests and summaries."""

from tg_auto_test.test_utils.file_processing_utils import build_file_message_payload, process_file_message_data
from tg_auto_test.test_utils.poll_vote_handler import create_callback_query_payload


def build_text_payload(client: object, text: str) -> tuple[dict[str, object], dict[str, object]]:
    """Build a serverless text update payload and request summary."""
    payload, msg = client._helpers.base_message_update(client._chat_id)  # noqa: SLF001
    msg["text"] = text
    if text.startswith("/"):
        msg["entities"] = [
            {"offset": 0, "length": text.find(" ") if " " in text else len(text), "type": "bot_command"},
        ]
    return payload, {"text": text}


def build_file_payload(  # noqa: PLR0913
    client: object,
    data: bytes,
    *,
    caption: str = "",
    force_document: bool = False,
    voice_note: bool = False,
    video_note: bool = False,
) -> tuple[dict[str, object], dict[str, object]]:
    """Build a serverless file update payload and request summary."""
    file_id = client._helpers.make_file_id()  # noqa: SLF001
    file_bytes, filename, content_type, file_data = process_file_message_data(
        data,
        caption=caption,
        force_document=force_document,
        voice_note=voice_note,
        video_note=video_note,
    )
    client._request.file_store[file_id] = file_data  # noqa: SLF001
    payload, msg = client._helpers.base_message_update(client._chat_id)  # noqa: SLF001
    build_file_message_payload(
        payload,
        msg,
        file_id,
        data,
        file_bytes,
        caption,
        force_document,
        voice_note,
        video_note,
    )
    file_kind = "document"
    if voice_note:
        file_kind = "voice"
    elif video_note:
        file_kind = "video_note"
    elif not force_document:
        file_kind = "photo"
    return payload, {
        "caption": caption,
        "content_type": content_type,
        "filename": filename,
        "kind": file_kind,
        "size_bytes": len(file_bytes),
    }


def build_callback_payload(client: object, message_id: int, data: str) -> tuple[dict[str, object], dict[str, object]]:
    """Build a callback query payload and request summary."""
    payload = create_callback_query_payload(
        message_id,
        data,
        client._chat_id,  # noqa: SLF001
        client._request._bot_user(),  # noqa: SLF001
        client._helpers,  # noqa: SLF001
    )
    return payload, {"callback_data": data, "message_id": message_id}


def build_poll_payload(
    client: object, message_id: int, option_ids: list[int]
) -> tuple[dict[str, object], dict[str, object]]:
    """Build a poll vote payload and request summary."""
    poll_data = client._poll_tracker.lookup_poll(message_id)  # noqa: SLF001
    if poll_data is None:
        raise RuntimeError(f"Poll not found for message_id {message_id}")
    _poll_id, option_mapping = poll_data
    invalid_ids = [option_id for option_id in option_ids if option_id not in option_mapping]
    if invalid_ids:
        raise RuntimeError(f"Invalid option ids for message_id {message_id}: {invalid_ids!r}")
    payload = {
        "update_id": client._helpers.next_update_id_value(),  # noqa: SLF001
        "poll_answer": {
            "poll_id": poll_data[0],
            "user": client._helpers.user_dict(),  # noqa: SLF001
            "option_ids": option_ids,
        },
    }
    return payload, {"message_id": message_id, "option_ids": option_ids}


async def run_payment_flow(client: object, message_id: int) -> None:
    """Simulate a Stars payment without using the client convenience wrappers."""
    if message_id not in client._invoices:  # noqa: SLF001
        raise RuntimeError(f"Unknown invoice message id: {message_id}")
    invoice = client._invoices[message_id]  # noqa: SLF001
    payload = str(invoice["payload"])
    currency = str(invoice["currency"])
    total_amount_raw = invoice["total_amount"]
    if not isinstance(total_amount_raw, int | str):
        raise RuntimeError(f"Invalid total_amount type for invoice {message_id}: {type(total_amount_raw)!r}")
    total_amount = int(total_amount_raw)
    if client._stars_balance < total_amount:  # noqa: SLF001
        raise RuntimeError("Insufficient Stars balance in serverless client.")
    pre_checkout_calls = await client._update_processor.process_update(  # noqa: SLF001
        client,
        {
            "update_id": client._helpers.next_update_id_value(),  # noqa: SLF001
            "pre_checkout_query": {
                "id": f"precheckout_{message_id}",
                "from": client._helpers.user_dict(),  # noqa: SLF001
                "currency": currency,
                "total_amount": total_amount,
                "invoice_payload": payload,
            },
        },
    )
    answers = [call for call in pre_checkout_calls if call.api_method == "answerPreCheckoutQuery"]
    if not answers or str(answers[-1].parameters.get("ok", "")).lower() != "true":
        raise RuntimeError(
            "Bot rejected the pre-checkout query." if answers else "Bot did not answer pre-checkout query."
        )
    await client._update_processor.process_update(  # noqa: SLF001
        client,
        {
            "update_id": client._helpers.next_update_id_value(),  # noqa: SLF001
            "message": {
                "message_id": client._helpers.next_message_id_value(),  # noqa: SLF001
                "date": 0,
                "chat": {"id": client._chat_id, "type": "private"},  # noqa: SLF001
                "from": client._helpers.user_dict(),  # noqa: SLF001
                "successful_payment": {
                    "currency": currency,
                    "invoice_payload": payload,
                    "provider_payment_charge_id": f"provider_charge_{message_id}",
                    "telegram_payment_charge_id": f"charge_{message_id}",
                    "total_amount": total_amount,
                },
            },
        },
    )
    client._stars_balance -= total_amount  # noqa: SLF001
