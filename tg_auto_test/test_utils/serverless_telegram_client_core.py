from collections import deque
from pathlib import Path
from typing import Union

from telegram import BotCommandScopeChat, MenuButtonDefault
from telegram.ext import Application
from telethon.tl.types import LabeledPrice, User

from tg_auto_test.test_utils.file_message_builder import build_file_payload
from tg_auto_test.test_utils.json_types import JsonValue
from tg_auto_test.test_utils.media_types import detect_content_type
from tg_auto_test.test_utils.models import FileData, ServerlessMessage, TelegramApiCall
from tg_auto_test.test_utils.poll_vote_handler import (
    PollTracker,
    create_callback_query_payload,
    handle_send_vote_request_for_client,
)
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
        self.request = StubTelegramRequest(bot_username=bot_username, bot_first_name=bot_first_name)
        builder = Application.builder().token(_FAKE_TOKEN).request(self.request)
        self.application = build_application(builder)
        self.chat_id, self.user_id, self.first_name = user_id, user_id, first_name
        self._helpers = ServerlessClientHelpers(user_id, first_name)
        self._connected = False
        self._outbox: deque[ServerlessMessage] = deque()
        self._stars_balance = 100
        self._invoices: dict[int, dict[str, str | int | list[LabeledPrice]]] = {}
        self._poll_tracker = PollTracker()
        self._stars_payment_handler = StarsPaymentHandler()
        self._update_processor = ServerlessUpdateProcessor()

    @property
    def api_calls(self) -> list[TelegramApiCall]:
        """Read-only view of all API calls made through this client."""
        return list(self.request.calls)

    @property
    def last_api_call(self) -> TelegramApiCall | None:
        """The last API call made through this client, or None if no calls were made."""
        return self.request.calls[-1] if self.request.calls else None

    async def connect(self) -> None:
        if not self._connected:
            await self.application.initialize()
            self._connected = True

    async def disconnect(self) -> None:
        if self._connected:
            await self.application.shutdown()
            self._connected = False

    async def get_me(self) -> User:
        return User(id=self.user_id, is_self=True, first_name=self.first_name, bot=False, access_hash=0)

    async def get_dialogs(self) -> list[str]:
        return []

    async def get_bot_state(self) -> dict[str, list[dict[str, str]] | str]:
        """Get bot state including commands and menu button type."""
        scope = BotCommandScopeChat(chat_id=self.chat_id)
        commands = await self.application.bot.get_my_commands(scope=scope)
        menu_btn = await self.application.bot.get_chat_menu_button(chat_id=self.chat_id)
        command_list = [{"command": cmd.command, "description": cmd.description} for cmd in commands]
        return {"commands": command_list, "menu_button_type": str(getattr(menu_btn, "type", "default"))}

    async def clear_bot_state(self) -> None:
        """Clear bot state including commands and menu button."""
        scope = BotCommandScopeChat(chat_id=self.chat_id)
        await self.application.bot.delete_my_commands(scope=scope)
        await self.application.bot.set_chat_menu_button(chat_id=self.chat_id, menu_button=MenuButtonDefault())

    async def get_messages(
        self, entity: str, ids: int | list[int]
    ) -> Union["TelethonCompatibleMessage", list["TelethonCompatibleMessage"], None]:
        """Get messages by ID(s) for Telethon compatibility."""
        del entity  # Not used in serverless mode
        if isinstance(ids, int):
            return TelethonCompatibleMessage(ids, self)
        return [TelethonCompatibleMessage(msg_id, self) for msg_id in ids]

    def conversation(self, bot_username: str, timeout: int = 10) -> ServerlessTelegramConversation:
        del bot_username, timeout
        return ServerlessTelegramConversation(client=self)

    def _pop_response(self) -> ServerlessMessage:
        if not self._outbox:
            raise RuntimeError("No pending response. Call send_message() first.")
        return self._outbox.popleft()

    async def _process_text_message(self, text: str) -> ServerlessMessage:
        self._outbox.clear()  # Auto-clear previous responses
        payload, msg = self._helpers.base_message_update(self.chat_id)
        msg["text"] = text
        if text.startswith("/"):
            cmd_len = text.find(" ") if " " in text else len(text)
            entity: dict[str, JsonValue] = {"offset": 0, "length": cmd_len, "type": "bot_command"}
            entities: list[JsonValue] = [entity]
            msg["entities"] = entities
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
        self._outbox.clear()  # Auto-clear previous responses
        file_id = self._helpers.make_file_id()
        file_bytes = file if isinstance(file, bytes) else file.read_bytes()
        fname = file.name if isinstance(file, Path) else "file"
        ct = detect_content_type(fname, force_document, voice_note, video_note)
        self.request.file_store[file_id] = FileData(data=file_bytes, filename=fname, content_type=ct)
        payload, msg = self._helpers.base_message_update(self.chat_id)
        build_file_payload(
            msg,
            file_id,
            file,
            file_bytes=file_bytes,
            caption=caption,
            force_document=force_document,
            voice_note=voice_note,
            video_note=video_note,
        )
        return await self._process_message_update(payload)

    async def _process_callback_query(self, message_id: int, data: str) -> ServerlessMessage:
        payload = create_callback_query_payload(
            message_id,
            data,
            self.chat_id,
            self.request._bot_user(),
            self._helpers,  # noqa: SLF001
        )
        return await self._process_message_update(payload)

    async def _handle_send_vote_request(
        self, peer: object, message_id: int, option_bytes: list[bytes]
    ) -> ServerlessMessage:
        """Handle Telethon SendVoteRequest by mapping to poll_answer update."""
        del peer  # Ignored in serverless mode
        return await handle_send_vote_request_for_client(
            self._poll_tracker,
            self._helpers,
            self._process_message_update,
            self._outbox,
            message_id,
            option_bytes,
        )

    async def _process_message_update(self, payload: dict[str, JsonValue]) -> ServerlessMessage:
        return await self._update_processor.process_message_update(self, payload)

    async def _process_update(self, payload: dict[str, JsonValue]) -> list[TelegramApiCall]:
        return await self._update_processor.process_update(self, payload)

    async def _handle_click(self, message_id: int, data: str) -> ServerlessMessage:
        outbox_before = len(self._outbox)
        result = await self._process_callback_query(message_id, data)
        while len(self._outbox) > outbox_before:
            self._outbox.pop()
        return result

    async def _simulate_stars_payment(self, invoice_message_id: int) -> None:
        self._stars_balance = await self._stars_payment_handler.simulate_payment(
            self, invoice_message_id, self._invoices, self._stars_balance, self._helpers
        )
