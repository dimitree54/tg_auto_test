from collections import deque
from pathlib import Path

from telegram.ext import Application
from telethon.tl.types import LabeledPrice

from tg_auto_test.test_utils.bot_state_utils import get_client_bot_state
from tg_auto_test.test_utils.file_processing_utils import (
    connect_client,
    disconnect_client,
    handle_click_wrapper,
    handle_send_vote_request_for_client_wrapper,
    pop_client_response,
    process_complete_file_message,
    simulate_stars_payment_wrapper,
)
from tg_auto_test.test_utils.json_types import JsonValue
from tg_auto_test.test_utils.models import ServerlessMessage, TelegramApiCall
from tg_auto_test.test_utils.poll_vote_handler import PollTracker, create_callback_query_payload
from tg_auto_test.test_utils.ptb_types import BuildApplication
from tg_auto_test.test_utils.serverless_client_helpers import ServerlessClientHelpers
from tg_auto_test.test_utils.serverless_client_public_api import ServerlessClientPublicAPI
from tg_auto_test.test_utils.serverless_stars_payment import StarsPaymentHandler
from tg_auto_test.test_utils.serverless_update_processor import ServerlessUpdateProcessor
from tg_auto_test.test_utils.stub_request import StubTelegramRequest

_FAKE_TOKEN = "123:ABC"


class ServerlessTelegramClientCore(ServerlessClientPublicAPI):
    def __init__(
        self,
        build_application: BuildApplication,
        user_id: int = 9001,
        first_name: str = "Alice",
        *,
        bot_username: str = "test_bot",
        bot_first_name: str = "TestBot",
    ) -> None:
        self._request = StubTelegramRequest(bot_username=bot_username, bot_first_name=bot_first_name)
        builder = Application.builder().token(_FAKE_TOKEN).request(self._request)
        self._application = build_application(builder)
        self._chat_id, self._user_id, self._first_name = user_id, user_id, first_name
        self._helpers = ServerlessClientHelpers(user_id, first_name)
        self._connected = False
        self._outbox: deque[ServerlessMessage] = deque()
        self._stars_balance = 100
        self._invoices: dict[int, dict[str, str | int | list[LabeledPrice]]] = {}
        self._poll_tracker = PollTracker()
        self._stars_payment_handler = StarsPaymentHandler()
        self._update_processor = ServerlessUpdateProcessor()

    @property
    def _api_calls(self) -> list[TelegramApiCall]:
        """Read-only view of all API calls made through this client."""
        return list(self._request.calls)

    @property
    def _last_api_call(self) -> TelegramApiCall | None:
        """The last API call made through this client, or None if no calls were made."""
        return self._request.calls[-1] if self._request.calls else None

    async def connect(self) -> None:
        await connect_client(self)

    async def disconnect(self) -> None:
        await disconnect_client(self)

    async def _get_bot_state(self) -> dict[str, list[dict[str, str]] | str]:
        return await get_client_bot_state(self._application, self._chat_id)

    def _pop_response(self) -> ServerlessMessage:
        return pop_client_response(self)  # type: ignore

    async def _process_text_message(self, text: str) -> ServerlessMessage:
        self._outbox.clear()
        payload, msg = self._helpers.base_message_update(self._chat_id)
        msg["text"] = text
        if text.startswith("/"):
            msg["entities"] = [
                {"offset": 0, "length": text.find(" ") if " " in text else len(text), "type": "bot_command"}
            ]
        return await self._process_message_update(payload)

    async def _process_file_message(
        self,
        file: Path | bytes,
        *,
        caption: str = "",
        force_document: bool = False,
        voice_note: bool = False,
        video_note: bool = False,
    ) -> ServerlessMessage:
        return await process_complete_file_message(
            self, file, caption=caption, force_document=force_document, voice_note=voice_note, video_note=video_note
        )  # type: ignore

    async def _process_callback_query(self, message_id: int, data: str) -> ServerlessMessage:
        return await self._process_message_update(
            create_callback_query_payload(message_id, data, self._chat_id, self._request._bot_user(), self._helpers)
        )

    async def _handle_send_vote_request(
        self, peer: object, message_id: int, option_bytes: list[bytes]
    ) -> ServerlessMessage:
        del peer
        return await handle_send_vote_request_for_client_wrapper(self, None, message_id, option_bytes)  # type: ignore

    async def _process_message_update(self, payload: dict[str, JsonValue]) -> ServerlessMessage:
        return await self._update_processor.process_message_update(self, payload)

    async def _handle_click(self, message_id: int, data: str) -> ServerlessMessage:
        return await handle_click_wrapper(self, message_id, data)  # type: ignore

    async def _simulate_stars_payment(self, invoice_message_id: int) -> None:
        await simulate_stars_payment_wrapper(self, invoice_message_id)
