"""Test reply markup (inline keyboard) handling with ServerlessTelegramClient."""

import pytest

from tests.unit.helpers_ptb_app import build_test_application
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


@pytest.mark.asyncio
async def test_inline_keyboard_markup() -> None:
    """Test that inline keyboard markup is properly returned."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/inline")
            msg = await conv.get_response()

            assert msg.text == "Choose:"
            assert msg._reply_markup_data is not None  # noqa: SLF001
            assert "inline_keyboard" in msg._reply_markup_data  # noqa: SLF001

            # Check that inline_keyboard contains the expected structure
            inline_keyboard = msg._reply_markup_data["inline_keyboard"]  # noqa: SLF001
            assert isinstance(inline_keyboard, list)
            assert len(inline_keyboard) == 1  # One row

            # Check the row contains two buttons
            row = inline_keyboard[0]
            assert isinstance(row, list)
            assert len(row) == 2

            # Check button structures
            btn_a, btn_b = row
            assert isinstance(btn_a, dict)
            assert isinstance(btn_b, dict)
            assert btn_a["text"] == "Option A"
            assert btn_a["callback_data"] == "opt_a"
            assert btn_b["text"] == "Option B"
            assert btn_b["callback_data"] == "opt_b"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_buttons_property() -> None:
    """Test the buttons property returns ServerlessButton objects."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/inline")
            msg = await conv.get_response()

            buttons = msg.buttons
            assert buttons is not None
            assert len(buttons) == 1  # One row

            # Check the row
            row = buttons[0]
            assert len(row) == 2  # Two buttons

            # Check individual buttons
            btn_a, btn_b = row
            assert btn_a.text == "Option A"
            assert btn_a._callback_data == "opt_a"  # noqa: SLF001
            assert btn_b.text == "Option B"
            assert btn_b._callback_data == "opt_b"  # noqa: SLF001
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_button_count_property() -> None:
    """Test the button_count property returns correct count."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/inline")
            msg = await conv.get_response()

            assert msg.button_count == 2
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_no_markup_returns_none() -> None:
    """Test that messages without markup have buttons=None."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("hello")
            msg = await conv.get_response()

            assert msg.buttons is None
            assert msg.button_count == 0
            assert msg._reply_markup_data is None  # noqa: SLF001
    finally:
        await client.disconnect()
