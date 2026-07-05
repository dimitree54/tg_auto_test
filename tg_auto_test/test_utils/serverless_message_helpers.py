"""Helper functions for ServerlessMessage."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from tg_auto_test.test_utils.json_types import JsonValue
from tg_auto_test.test_utils.serverless_bot_callback_answer import ServerlessBotCallbackAnswer
from tg_auto_test.test_utils.serverless_button import ServerlessButton

ReplyMarkup = dict[str, JsonValue]
ClickCallback = Callable[[int, str], Awaitable[ServerlessBotCallbackAnswer]]
ButtonTextSelector = str | Callable[[str], bool]
ButtonFilter = Callable[[ServerlessButton], bool]


@dataclass(frozen=True, slots=True)
class FileData:
    """Binary payload attached to an outgoing Telegram API call."""

    data: bytes
    filename: str = ""
    content_type: str = "application/octet-stream"


def _wrap_button_row(row: JsonValue) -> list[ServerlessButton]:
    """Convert a raw JSON row of buttons into ServerlessButton objects."""
    if not isinstance(row, list):
        return []

    return [
        ServerlessButton(text=str(btn["text"]), _callback_data=str(btn.get("callback_data", "")))
        for btn in row
        if isinstance(btn, dict)
    ]


def resolve_click_data(
    buttons: list[list[ServerlessButton]] | None,
    i: int | None,
    j: int | None,
    text: ButtonTextSelector | None,
    button_filter: ButtonFilter | None,
) -> bytes:
    """Resolve Telethon-style button selectors to callback data bytes."""
    if buttons is None:
        raise ValueError("message has no buttons")
    if sum(selector is not None for selector in (i, text, button_filter)) >= 2:
        raise ValueError("You can only set either of i, text or filter")

    button = _find_button(buttons, i=i, j=j, text=text, button_filter=button_filter)
    if button is None:
        raise ValueError("no matching button found")
    if not button.data:
        raise ValueError("selected button has no callback data")
    return button.data


def _find_button(
    buttons: list[list[ServerlessButton]],
    i: int | None,
    j: int | None,
    text: ButtonTextSelector | None,
    button_filter: ButtonFilter | None,
) -> ServerlessButton | None:
    if text is not None:
        return _find_button_by_text(_flatten_buttons(buttons), text)
    if button_filter is not None:
        return _find_button_by_filter(_flatten_buttons(buttons), button_filter)
    return _find_button_by_index(buttons, i=i, j=j)


def _find_button_by_text(buttons: list[ServerlessButton], text: ButtonTextSelector) -> ServerlessButton | None:
    if callable(text):
        for button in buttons:
            if text(button.text):
                return button
        return None
    for button in buttons:
        if button.text == text:
            return button
    return None


def _find_button_by_filter(buttons: list[ServerlessButton], button_filter: ButtonFilter) -> ServerlessButton | None:
    for button in buttons:
        if button_filter(button):
            return button
    return None


def _find_button_by_index(
    buttons: list[list[ServerlessButton]],
    i: int | None,
    j: int | None,
) -> ServerlessButton:
    row_index = 0 if i is None else i
    if j is not None:
        return buttons[row_index][j]
    return _flatten_buttons(buttons)[row_index]


def _flatten_buttons(buttons: list[list[ServerlessButton]]) -> list[ServerlessButton]:
    return [button for row in buttons for button in row]
