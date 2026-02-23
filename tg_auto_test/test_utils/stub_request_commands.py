import json

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


class CommandMenuMixin:
    _scoped_commands: dict[str, list[dict[str, str]]]
    _menu_button: dict[str, str] | None

    def _handle_set_my_commands(self, parameters: dict[str, str]) -> tuple[int, bytes]:
        raw = parameters.get("commands", "[]")
        commands = json.loads(raw) if isinstance(raw, str) else []
        key = _scope_key(parameters)
        self._scoped_commands[key] = commands
        return self._ok_response(True)  # type: ignore[attr-defined]

    def _handle_get_my_commands(self, parameters: dict[str, str]) -> tuple[int, bytes]:
        key = _scope_key(parameters)
        commands = self._scoped_commands.get(key, [])
        return self._ok_response(commands)  # type: ignore[attr-defined]

    def _handle_delete_my_commands(self, parameters: dict[str, str]) -> tuple[int, bytes]:
        key = _scope_key(parameters)
        self._scoped_commands.pop(key, None)
        return self._ok_response(True)  # type: ignore[attr-defined]

    def _handle_set_chat_menu_button(self, parameters: dict[str, str]) -> tuple[int, bytes]:
        raw = parameters.get("menu_button")
        self._menu_button = json.loads(raw) if isinstance(raw, str) else None
        return self._ok_response(True)  # type: ignore[attr-defined]

    def _handle_get_chat_menu_button(self, _parameters: dict[str, str]) -> tuple[int, bytes]:
        if self._menu_button is None:
            return self._ok_response({"type": "default"})  # type: ignore[attr-defined]
        return self._ok_response(self._menu_button)  # type: ignore[attr-defined]

    def _handle_answer_callback_query(self, _parameters: dict[str, str]) -> tuple[int, bytes]:
        return self._ok_response(True)  # type: ignore[attr-defined]

    def _handle_edit_message_text(self, parameters: dict[str, str]) -> tuple[int, bytes]:
        msg: dict[str, JsonValue] = self._base_message(parameters)  # type: ignore[attr-defined]
        msg["text"] = parameters.get("text", "")
        return self._ok_response(msg)  # type: ignore[attr-defined]
