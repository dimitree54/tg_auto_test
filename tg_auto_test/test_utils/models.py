"""Data models for the serverless Telegram testing infrastructure.

Re-exports all public models from decomposed files.
"""

from dataclasses import dataclass

from tg_auto_test.test_utils.json_types import JsonValue
from tg_auto_test.test_utils.serverless_button import ServerlessButton
from tg_auto_test.test_utils.serverless_message import ServerlessMessage
from tg_auto_test.test_utils.serverless_message_helpers import (
    ClickCallback,
    FileData,
    ReplyMarkup,
    _wrap_button_row,
)


@dataclass(frozen=True, slots=True)
class TelegramApiCall:
    """Record of a single outgoing Telegram Bot API call."""

    api_method: str
    parameters: dict[str, str]
    file: FileData | None = None
    result: JsonValue | None = None


# Re-export all public symbols
__all__ = [
    "ServerlessButton",
    "ServerlessMessage",
    "FileData",
    "TelegramApiCall",
    "ReplyMarkup",
    "ClickCallback",
    "_wrap_button_row",
]
