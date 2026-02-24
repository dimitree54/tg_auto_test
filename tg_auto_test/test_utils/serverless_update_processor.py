from telegram import Update

from tg_auto_test.test_utils.json_types import JsonValue
from tg_auto_test.test_utils.models import ServerlessMessage, TelegramApiCall
from tg_auto_test.test_utils.response_processor import extract_responses


class ServerlessUpdateProcessor:
    """Handles update processing for serverless clients."""

    async def process_update(
        self,
        client: "ServerlessTelegramClientCore",
        payload: dict[str, JsonValue],
    ) -> list[TelegramApiCall]:
        if not client._connected:  # noqa: SLF001
            raise RuntimeError("Call connect() before processing payloads.")
        calls_before = len(client.request.calls)
        update = Update.de_json(payload, client.application.bot)
        await client.application.process_update(update)
        return client.request.calls[calls_before:]

    async def process_message_update(
        self,
        client: "ServerlessTelegramClientCore",
        payload: dict[str, JsonValue],
    ) -> ServerlessMessage:
        new_calls = await self.process_update(client, payload)
        responses = extract_responses(
            new_calls,
            client.request.file_store,
            client._invoices,
            client._handle_click,
            client._poll_tracker,  # noqa: SLF001
        )
        if not responses:
            raise RuntimeError("Bot did not send a recognizable response.")
        for resp in responses:
            client._outbox.append(resp)  # noqa: SLF001
        return responses[-1]
