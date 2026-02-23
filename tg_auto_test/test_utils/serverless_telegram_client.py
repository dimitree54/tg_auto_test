from telethon.tl.types import InputPeerUser

from tg_auto_test.test_utils.ptb_types import BuildApplication
from tg_auto_test.test_utils.serverless_telegram_client_core import ServerlessTelegramClientCore
from tg_auto_test.test_utils.serverless_telethon_rpc import (
    TelethonRequest,
    TelethonResponse,
    handle_telethon_request,
)


class ServerlessTelegramClient(ServerlessTelegramClientCore):
    def __init__(
        self,
        build_application: BuildApplication,
        user_id: int = 9001,
        first_name: str = "Alice",
        *,
        bot_username: str = "test_bot",
        bot_first_name: str = "TestBot",
    ) -> None:
        super().__init__(
            build_application=build_application,
            user_id=user_id,
            first_name=first_name,
            bot_username=bot_username,
            bot_first_name=bot_first_name,
        )

    async def get_input_entity(self, entity: str) -> InputPeerUser:
        del entity
        return InputPeerUser(user_id=999_999, access_hash=0)

    async def __call__(self, request: TelethonRequest) -> TelethonResponse:
        return await handle_telethon_request(self, request)

    async def simulate_stars_payment(self, invoice_message_id: int) -> None:
        if invoice_message_id not in self._invoices:
            raise RuntimeError(f"Unknown invoice message id: {invoice_message_id}")
        invoice = self._invoices[invoice_message_id]
        payload = str(invoice["payload"])
        currency = str(invoice["currency"])
        total_amount_raw = invoice["total_amount"]
        if not isinstance(total_amount_raw, int | str):
            raise RuntimeError(
                f"Invalid total_amount type for invoice {invoice_message_id}: {type(total_amount_raw)!r}"
            )
        total_amount = int(total_amount_raw)
        if self._stars_balance < total_amount:
            raise RuntimeError("Insufficient Stars balance in serverless client.")
        self._stars_balance -= total_amount

        pre_checkout_calls = await self._process_update({
            "update_id": self._next_update_id_value(),
            "pre_checkout_query": {
                "id": f"precheckout_{invoice_message_id}",
                "from": self._user_dict(),
                "currency": currency,
                "total_amount": total_amount,
                "invoice_payload": payload,
            },
        })
        answers = [call for call in pre_checkout_calls if call.api_method == "answerPreCheckoutQuery"]
        if not answers:
            raise RuntimeError("Bot did not answer pre-checkout query.")
        ok = str(answers[-1].parameters.get("ok", "")).lower() == "true"
        if not ok:
            raise RuntimeError("Bot rejected the pre-checkout query.")

        await self._process_message_update({
            "update_id": self._next_update_id_value(),
            "message": {
                "message_id": self._next_message_id_value(),
                "date": 0,
                "chat": {"id": self.chat_id, "type": "private"},
                "from": self._user_dict(),
                "successful_payment": {
                    "currency": currency,
                    "total_amount": total_amount,
                    "invoice_payload": payload,
                    "telegram_payment_charge_id": f"charge_{invoice_message_id}",
                    "provider_payment_charge_id": f"provider_charge_{invoice_message_id}",
                },
            },
        })
