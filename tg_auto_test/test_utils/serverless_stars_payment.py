from telethon.tl.types import LabeledPrice


class StarsPaymentHandler:
    """Handles Stars payment simulation for serverless clients."""

    async def simulate_payment(
        self,
        client: "ServerlessTelegramClientCore",
        invoice_message_id: int,
        invoices: dict[int, dict[str, str | int | list[LabeledPrice]]],
        stars_balance: int,
        helpers: "ServerlessClientHelpers",
    ) -> int:
        """Simulate Stars payment processing and return the new balance."""
        if invoice_message_id not in invoices:
            raise RuntimeError(f"Unknown invoice message id: {invoice_message_id}")
        invoice = invoices[invoice_message_id]
        payload, currency = str(invoice["payload"]), str(invoice["currency"])
        total_amount_raw = invoice["total_amount"]
        if not isinstance(total_amount_raw, int | str):
            raise RuntimeError(
                f"Invalid total_amount type for invoice {invoice_message_id}: {type(total_amount_raw)!r}"
            )
        total_amount = int(total_amount_raw)
        if stars_balance < total_amount:
            raise RuntimeError("Insufficient Stars balance in serverless client.")
        new_balance = stars_balance - total_amount

        pre_checkout_calls = await client._process_update({  # noqa: SLF001
            "update_id": helpers.next_update_id_value(),
            "pre_checkout_query": {
                "id": f"precheckout_{invoice_message_id}",
                "from": helpers.user_dict(),
                "currency": currency,
                "total_amount": total_amount,
                "invoice_payload": payload,
            },
        })
        answers = [call for call in pre_checkout_calls if call.api_method == "answerPreCheckoutQuery"]
        if not answers or str(answers[-1].parameters.get("ok", "")).lower() != "true":
            err_msg = (
                "Bot did not answer pre-checkout query." if not answers else "Bot rejected the pre-checkout query."
            )
            raise RuntimeError(err_msg)

        await client._process_message_update({  # noqa: SLF001
            "update_id": helpers.next_update_id_value(),
            "message": {
                "message_id": helpers.next_message_id_value(),
                "date": 0,
                "chat": {"id": client._chat_id, "type": "private"},  # noqa: SLF001
                "from": helpers.user_dict(),
                "successful_payment": {
                    "currency": currency,
                    "total_amount": total_amount,
                    "invoice_payload": payload,
                    "telegram_payment_charge_id": f"charge_{invoice_message_id}",
                    "provider_payment_charge_id": f"provider_charge_{invoice_message_id}",
                },
            },
        })

        return new_balance
