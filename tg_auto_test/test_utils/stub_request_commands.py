import json
from typing import Protocol

from tg_auto_test.test_utils.html_parser import parse_html
from tg_auto_test.test_utils.json_types import JsonValue


def _scope_key(parameters: dict[str, str]) -> str:
    raw = parameters.get("scope")
    if raw is None:
        return "default"
    scope = json.loads(raw) if isinstance(raw, str) else raw
    scope_type = scope.get("type", "default")
    if scope_type == "chat":
        return f"chat:{scope['chat_id']}"
    return scope_type


class _CommandMenuHost(Protocol):
    _scoped_commands: dict[str, list[dict[str, str]]]
    _menu_button: dict[str, str] | None

    def _base_message(self, parameters: dict[str, str]) -> dict[str, JsonValue]: ...

    def _edit_message(self, parameters: dict[str, str]) -> dict[str, JsonValue]: ...

    def _ok_response(self, result: JsonValue) -> tuple[int, bytes]: ...


class CommandMenuMixin:
    def _handle_set_my_commands(self: _CommandMenuHost, parameters: dict[str, str]) -> tuple[int, bytes]:
        raw = parameters.get("commands", "[]")
        commands = json.loads(raw) if isinstance(raw, str) else []
        key = _scope_key(parameters)
        self._scoped_commands[key] = commands
        return self._ok_response(True)

    def _handle_get_my_commands(self: _CommandMenuHost, parameters: dict[str, str]) -> tuple[int, bytes]:
        key = _scope_key(parameters)
        commands = self._scoped_commands.get(key, [])
        return self._ok_response(commands)

    def _handle_delete_my_commands(self: _CommandMenuHost, parameters: dict[str, str]) -> tuple[int, bytes]:
        key = _scope_key(parameters)
        self._scoped_commands.pop(key, None)
        return self._ok_response(True)

    def _handle_set_chat_menu_button(self: _CommandMenuHost, parameters: dict[str, str]) -> tuple[int, bytes]:
        raw = parameters.get("menu_button")
        self._menu_button = json.loads(raw) if isinstance(raw, str) else None
        return self._ok_response(True)

    def _handle_get_chat_menu_button(self: _CommandMenuHost, _parameters: dict[str, str]) -> tuple[int, bytes]:
        if self._menu_button is None:
            return self._ok_response({"type": "default"})
        return self._ok_response(self._menu_button)

    def _handle_answer_callback_query(self: _CommandMenuHost, _parameters: dict[str, str]) -> tuple[int, bytes]:
        return self._ok_response(True)

    def _handle_edit_message_text(self: _CommandMenuHost, parameters: dict[str, str]) -> tuple[int, bytes]:
        msg: dict[str, JsonValue] = self._edit_message(parameters)
        raw_text = parameters.get("text", "")
        parse_mode = parameters.get("parse_mode", "")
        if parse_mode.lower() == "html":
            text, entities = parse_html(raw_text)
            msg["text"] = text
            if entities:
                msg["entities"] = entities
        else:
            msg["text"] = raw_text
        return self._ok_response(msg)
