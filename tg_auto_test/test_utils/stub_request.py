from collections.abc import Callable
import json

from telegram.request import BaseRequest, RequestData

from tg_auto_test.test_utils.html_parser import parse_html
from tg_auto_test.test_utils.json_types import JsonValue
from tg_auto_test.test_utils.media_types import MEDIA_PARAM_KEY
from tg_auto_test.test_utils.models import FileData, TelegramApiCall
from tg_auto_test.test_utils.stub_request_commands import CommandMenuMixin
from tg_auto_test.test_utils.stub_request_media import MediaMixin

_FILE_PATH_PREFIX = "/file/bot"


def _apply_parse_mode(parameters: dict[str, str], text_key: str = "text") -> tuple[str, list[dict[str, JsonValue]]]:
    """Parse HTML/Markdown formatting when parse_mode is set."""
    raw_text = parameters.get(text_key, "")
    parse_mode = parameters.get("parse_mode", "")
    if parse_mode.lower() == "html":
        return parse_html(raw_text)
    return raw_text, []


class StubTelegramRequest(CommandMenuMixin, MediaMixin, BaseRequest):
    TelegramApiHandler = Callable[[dict[str, str]], tuple[int, bytes]]

    def __init__(self, *, bot_username: str = "test_bot", bot_first_name: str = "TestBot") -> None:
        super().__init__()
        self.calls: list[TelegramApiCall] = []
        self.file_store: dict[str, FileData] = {}
        self._next_message_id = 1
        self._generated_file_id_counter = 1
        self._next_poll_id = 1
        self._scoped_commands: dict[str, list[dict[str, str]]] = {}
        self._menu_button: dict[str, str] | None = None
        self._bot_username = bot_username
        self._bot_first_name = bot_first_name
        self._handlers: dict[str, StubTelegramRequest.TelegramApiHandler] = {
            "getMe": self._handle_get_me,
            "getFile": self._handle_get_file,
            "sendMessage": self._handle_send_message,
            "sendDocument": self._handle_send_media,
            "sendVoice": self._handle_send_media,
            "sendPhoto": self._handle_send_media,
            "sendVideoNote": self._handle_send_media,
            "sendVideo": self._handle_send_media,
            "sendAnimation": self._handle_send_media,
            "sendAudio": self._handle_send_media,
            "sendSticker": self._handle_send_media,
            "sendInvoice": self._handle_send_invoice,
            "answerPreCheckoutQuery": self._handle_ack,
            "sendChatAction": self._handle_ack,
            "setMyCommands": self._handle_set_my_commands,
            "getMyCommands": self._handle_get_my_commands,
            "deleteMyCommands": self._handle_delete_my_commands,
            "setChatMenuButton": self._handle_set_chat_menu_button,
            "getChatMenuButton": self._handle_get_chat_menu_button,
            "answerCallbackQuery": self._handle_answer_callback_query,
            "editMessageText": self._handle_edit_message_text,
            "deleteMessage": self._handle_ack,
            "sendPoll": self._handle_send_poll,
        }

    @property
    def read_timeout(self) -> float | None:
        return None

    async def initialize(self) -> None:
        return None

    async def shutdown(self) -> None:
        return None

    async def do_request(
        self,
        url: str,
        method: str,
        request_data: RequestData | None = None,
        read_timeout: float | None = None,
        write_timeout: float | None = None,
        connect_timeout: float | None = None,
        pool_timeout: float | None = None,
    ) -> tuple[int, bytes]:
        del method, read_timeout, write_timeout, connect_timeout, pool_timeout

        file_download_idx = url.find(_FILE_PATH_PREFIX)
        if file_download_idx != -1:
            return self._handle_file_download(url[file_download_idx:])

        api_method = url.rsplit("/", 1)[-1]
        parameters = {} if request_data is None else dict(request_data.json_parameters)

        file_data = self._extract_file(api_method, request_data, parameters)
        self.calls.append(TelegramApiCall(api_method=api_method, parameters=parameters, file=file_data))

        handler = self._handlers.get(api_method)
        if handler is None:
            raise AssertionError(f"Unexpected Telegram API method: {api_method}")
        status_code, payload = handler(parameters)
        result: JsonValue | None = None
        if status_code == 200:
            body = json.loads(payload)
            result = body.get("result")
        self.calls[-1] = TelegramApiCall(api_method=api_method, parameters=parameters, file=file_data, result=result)
        return status_code, payload

    def _extract_file(
        self, api_method: str, request_data: RequestData | None, parameters: dict[str, str]
    ) -> FileData | None:
        """Extract uploaded file bytes from multipart data."""
        if request_data is None or not request_data.contains_files:
            return None
        param_key = MEDIA_PARAM_KEY.get(api_method)
        if param_key is None:
            return None
        multipart = request_data.multipart_data
        if param_key not in multipart:
            return None
        entry = multipart[param_key]
        filename, payload_data, content_type = entry[0], entry[1], entry[2]
        raw_bytes = payload_data if isinstance(payload_data, bytes) else payload_data.read()
        generated_id = f"stub_generated_{self._generated_file_id_counter}"
        self._generated_file_id_counter += 1
        parameters[param_key] = generated_id
        return FileData(data=raw_bytes, filename=filename, content_type=content_type)

    def _handle_file_download(self, file_path: str) -> tuple[int, bytes]:
        file_id = file_path.rsplit("/", 1)[-1]
        if file_id not in self.file_store:
            raise AssertionError(f"No file bytes stored for file_id={file_id}")
        return 200, self.file_store[file_id].data

    def _handle_get_me(self, _parameters: dict[str, str]) -> tuple[int, bytes]:
        return self._ok_response(self._bot_user())

    def _handle_get_file(self, parameters: dict[str, str]) -> tuple[int, bytes]:
        file_id = parameters["file_id"]
        return self._ok_response({
            "file_id": file_id,
            "file_unique_id": f"unique_{file_id}",
            "file_path": f"photos/{file_id}",
        })

    def _handle_send_message(self, parameters: dict[str, str]) -> tuple[int, bytes]:
        msg = self._base_message(parameters)
        text, entities = _apply_parse_mode(parameters)
        msg["text"] = text
        if entities:
            msg["entities"] = entities
        if "reply_markup" in parameters:
            markup = json.loads(parameters["reply_markup"])
            # Only include InlineKeyboardMarkup in the response (Telegram API spec).
            # ReplyKeyboardMarkup is consumed by the client, not echoed back.
            if "inline_keyboard" in markup:
                msg["reply_markup"] = markup
        return self._ok_response(msg)

    def _handle_ack(self, _parameters: dict[str, str]) -> tuple[int, bytes]:
        return self._ok_response(True)

    def _base_message(self, parameters: dict[str, str]) -> dict[str, JsonValue]:
        message_id = self._next_message_id
        self._next_message_id += 1
        chat_id = int(parameters["chat_id"])
        return {
            "message_id": message_id,
            "date": 0,
            "chat": {"id": chat_id, "type": "private"},
            "from": self._bot_user(),
        }

    def _edit_message(self, parameters: dict[str, str]) -> dict[str, JsonValue]:
        message_id = int(parameters["message_id"])
        chat_id = int(parameters["chat_id"])
        return {
            "message_id": message_id,
            "date": 0,
            "chat": {"id": chat_id, "type": "private"},
            "from": self._bot_user(),
        }

    def _bot_user(self) -> dict[str, JsonValue]:
        return {"id": 999_999, "is_bot": True, "first_name": self._bot_first_name, "username": self._bot_username}

    def get_scoped_commands(self, key: str) -> list[dict[str, str]]:
        """Get scoped commands for a given scope key."""
        return self._scoped_commands.get(key, [])

    def get_menu_button(self) -> dict[str, str] | None:
        """Get the current menu button."""
        return self._menu_button

    @staticmethod
    def _ok_response(result: JsonValue) -> tuple[int, bytes]:
        body = {"ok": True, "result": result}
        return 200, json.dumps(body).encode()
