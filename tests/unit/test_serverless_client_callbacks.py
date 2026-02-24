"""Test inline button callback handling with ServerlessTelegramClient."""

from typing import cast

import pytest

from tests.unit.helpers_ptb_app import build_test_application
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient
from tg_auto_test.test_utils.telethon_compatible_message import TelethonCompatibleMessage


@pytest.mark.asyncio
async def test_inline_button_click() -> None:
    """Test clicking inline buttons and receiving callback responses."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            # Send command to get inline keyboard
            await conv.send_message("/inline")
            msg_with_buttons = await conv.get_response()

            assert msg_with_buttons.text == "Choose:"
            assert msg_with_buttons.buttons is not None
            assert msg_with_buttons.button_count == 2

            # Click the first button (Option A)
            response_msg = await msg_with_buttons.click(data=b"opt_a")

            assert response_msg.text == "You chose: opt_a"
            assert isinstance(response_msg.id, int)
            assert response_msg.id > 0
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_different_callback_data() -> None:
    """Test clicking different buttons produces different responses."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            # Get inline keyboard
            await conv.send_message("/inline")
            msg_with_buttons = await conv.get_response()

            # Click Option A
            response_a = await msg_with_buttons.click(data=b"opt_a")
            assert response_a.text == "You chose: opt_a"

            # Get keyboard again
            await conv.send_message("/inline")
            msg_with_buttons2 = await conv.get_response()

            # Click Option B
            response_b = await msg_with_buttons2.click(data=b"opt_b")
            assert response_b.text == "You chose: opt_b"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_click_via_get_messages() -> None:
    """Test clicking buttons via get_messages + message.click() (Telethon pattern)."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/inline")
            msg_with_buttons = await conv.get_response()

            # Use Telethon pattern: get message, then click
            message = await client.get_messages("test_bot", ids=msg_with_buttons.id)
            message = cast(TelethonCompatibleMessage, message)
            response_msg = await message.click(data=b"opt_a")

            assert response_msg.text == "You chose: opt_a"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_click_on_message_without_buttons() -> None:
    """Test that clicking messages without buttons still works (sends callback query)."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            # Send regular text message (no buttons)
            await conv.send_message("hello")
            msg = await conv.get_response()

            assert msg.buttons is None
            assert msg.text == "hello"

            # Clicking should work and trigger the callback handler
            # even though the message has no buttons
            response = await msg.click(data=b"test_data")

            # The callback handler should respond with the callback data
            assert "You chose: test_data" in response.text
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_button_properties_match_click_data() -> None:
    """Test that button properties match what we can click."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/inline")
            msg = await conv.get_response()

            assert msg.buttons is not None
            assert len(msg.buttons) == 1  # One row
            row = msg.buttons[0]
            assert len(row) == 2  # Two buttons

            # Test clicking the callback_data from button properties
            btn_a, btn_b = row

            # Click using the callback_data from button A
            response = await msg.click(data=btn_a.callback_data.encode())
            assert response.text == "You chose: opt_a"

            # Get new keyboard message
            await conv.send_message("/inline")
            msg2 = await conv.get_response()

            # Click using the callback_data from button B
            response2 = await msg2.click(data=btn_b.callback_data.encode())
            assert response2.text == "You chose: opt_b"
    finally:
        await client.disconnect()
