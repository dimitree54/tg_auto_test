from collections import deque
from pathlib import Path
from typing import Union

from telegram.ext import Application
from telethon.tl.types import LabeledPrice, User

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
from tg_auto_test.test_utils.serverless_stars_payment import StarsPaymentHandler
from tg_auto_test.test_utils.serverless_telegram_conversation import ServerlessTelegramConversation
from tg_auto_test.test_utils.serverless_update_processor import ServerlessUpdateProcessor
from tg_auto_test.test_utils.stub_request import StubTelegramRequest
from tg_auto_test.test_utils.telethon_compatible_message import TelethonCompatibleMessage

_FAKE_TOKEN = "123:ABC"


class ServerlessTelegramClientCore:
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

    async def get_me(self, input_peer: bool = False) -> User:
        if input_peer is True:
            raise NotImplementedError("input_peer=True not supported")
        return User(id=self._user_id, is_self=True, first_name=self._first_name, bot=False, access_hash=0)

    async def get_dialogs(
        self,
        limit: int | None = None,
        *,
        offset_date: object = None,
        offset_id: int = 0,
        offset_peer: object = None,
        ignore_pinned: bool = False,
        ignore_migrated: bool = False,
        folder: int | None = None,
        archived: bool = False,
    ) -> list[object]:
        del limit, offset_date, offset_id, offset_peer, ignore_pinned, ignore_migrated, folder, archived
        return []

    async def _get_bot_state(self) -> dict[str, list[dict[str, str]] | str]:
        return await get_client_bot_state(self._application, self._chat_id)

    async def get_messages(
        self,
        entity: object,
        limit: int | None = None,
        *,
        offset_date: object = None,
        offset_id: int = 0,
        max_id: int = 0,
        min_id: int = 0,
        add_offset: int = 0,
        search: str | None = None,
        filter: object = None,
        from_user: object = None,
        wait_time: float | None = None,
        ids: int | list[int] | None = None,
        reverse: bool = False,
        reply_to: int | None = None,
        scheduled: bool = False,
    ) -> Union["TelethonCompatibleMessage", list["TelethonCompatibleMessage"], None]:
        del entity
        if ids is None and limit is None:
            raise ValueError("Either 'ids' or 'limit' must be provided")
        if [
            limit,
            offset_date,
            offset_id,
            max_id,
            min_id,
            add_offset,
            search,
            filter,
            from_user,
            wait_time,
            reverse,
            reply_to,
            scheduled,
        ] != [None, None, 0, 0, 0, 0, None, None, None, None, False, None, False]:
            raise NotImplementedError("Parameter not supported")
        return (
            TelethonCompatibleMessage(ids, self)
            if isinstance(ids, int)
            else ([TelethonCompatibleMessage(msg_id, self) for msg_id in ids] if ids is not None else None)
        )

    def conversation(
        self,
        entity: object,
        *,
        timeout: float = 60.0,
        total_timeout: float | None = None,
        max_messages: int = 100,
        exclusive: bool = True,
        replies_are_responses: bool = True,
    ) -> ServerlessTelegramConversation:
        del entity, timeout
        if [total_timeout, max_messages, exclusive, replies_are_responses] != [None, 100, True, True]:
            raise NotImplementedError("Parameter not supported")
        return ServerlessTelegramConversation(client=self)

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

    async def _process_update(self, payload: dict[str, JsonValue]) -> list[TelegramApiCall]:
        return await self._update_processor.process_update(self, payload)

    async def _handle_click(self, message_id: int, data: str) -> ServerlessMessage:
        return await handle_click_wrapper(self, message_id, data)  # type: ignore

    async def _simulate_stars_payment(self, invoice_message_id: int) -> None:
        await simulate_stars_payment_wrapper(self, invoice_message_id)
