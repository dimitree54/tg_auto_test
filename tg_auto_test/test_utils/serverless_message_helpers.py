"""Helper functions for ServerlessMessage."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from tg_auto_test.test_utils.json_types import JsonValue

ReplyMarkup = dict[str, JsonValue]
ClickCallback = Callable[[int, str], Awaitable["ServerlessMessage"]]


@dataclass(frozen=True, slots=True)
class FileData:
    """Binary payload attached to an outgoing Telegram API call."""

    data: bytes
    filename: str = ""
    content_type: str = "application/octet-stream"


def _wrap_button_row(row: JsonValue) -> list[object]:
    """Convert a raw JSON row of buttons into ServerlessButton objects."""
    if not isinstance(row, list):
        return []

    # Import here to avoid circular imports - this is the recommended pattern for this codebase
    from tg_auto_test.test_utils.serverless_button import ServerlessButton  # noqa: PLC0415

    return [
        ServerlessButton(text=str(btn["text"]), _callback_data=str(btn.get("callback_data", "")))
        for btn in row
        if isinstance(btn, dict)
    ]
