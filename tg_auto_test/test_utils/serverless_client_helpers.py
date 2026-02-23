"""Helper utilities for the serverless Telegram client."""

from tg_auto_test.test_utils.json_types import JsonValue


class ServerlessClientHelpers:
    """Helper utilities for generating IDs and common data structures."""

    def __init__(self, user_id: int, first_name: str) -> None:
        self.user_id = user_id
        self.first_name = first_name
        self._next_update_id = 1
        self._next_message_id = 1
        self._file_id_counter = 1

    def next_update_id_value(self) -> int:
        """Generate next update ID."""
        val, self._next_update_id = self._next_update_id, self._next_update_id + 1
        return val

    def next_message_id_value(self) -> int:
        """Generate next message ID."""
        val, self._next_message_id = self._next_message_id, self._next_message_id + 1
        return val

    def user_dict(self) -> dict[str, JsonValue]:
        """Generate user dictionary for API payloads."""
        return {"id": self.user_id, "is_bot": False, "first_name": self.first_name}

    def make_file_id(self) -> str:
        """Generate a unique file ID."""
        fid = f"stub_file_{self._file_id_counter}"
        self._file_id_counter += 1
        return fid

    def base_message_update(self, chat_id: int) -> tuple[dict[str, JsonValue], dict[str, JsonValue]]:
        """Create base message update payload and message dict."""
        message: dict[str, JsonValue] = {
            "message_id": self.next_message_id_value(),
            "date": 0,
            "chat": {"id": chat_id, "type": "private"},
            "from": self.user_dict(),
        }
        payload: dict[str, JsonValue] = {
            "update_id": self.next_update_id_value(),
            "message": message,
        }
        return payload, message
