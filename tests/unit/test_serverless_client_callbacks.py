"""Test inline button callback handling with ServerlessTelegramClient."""

from typing import cast

import pytest

from tests.unit.helpers_ptb_app import build_test_application
from tg_auto_test.test_utils.models import ServerlessMessage
from tg_auto_test.test_utils.serverless_bot_callback_answer import ServerlessBotCallbackAnswer
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


@pytest.mark.asyncio
async def test_inline_button_click() -> None:
    """Test clicking inline buttons and receiving callback responses via get_response()."""
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

            # click() returns a BotCallbackAnswer, matching Telethon behaviour
            answer = await msg_with_buttons.click(data=b"opt_a")
            assert isinstance(answer, ServerlessBotCallbackAnswer)

            # Bot response message is available via get_response(), matching Telethon
            response_msg = await conv.get_response()
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

            # Click Option A — response available via get_response()
            await msg_with_buttons.click(data=b"opt_a")
            response_a = await conv.get_response()
            assert response_a.text == "You chose: opt_a"

            # Get keyboard again
            await conv.send_message("/inline")
            msg_with_buttons2 = await conv.get_response()

            # Click Option B
            await msg_with_buttons2.click(data=b"opt_b")
            response_b = await conv.get_response()
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
            assert message is not None
            message = cast(ServerlessMessage, message)  # get_messages with single int returns single ServerlessMessage
            await message.click(data=b"opt_a")

            # Bot response is in the outbox, retrieve it with get_response()
            response_msg = await conv.get_response()
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
            await msg.click(data=b"test_data")

            # The callback handler should respond with the callback data
            response = await conv.get_response()
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
            await msg.click(data=btn_a.data)
            response = await conv.get_response()
            assert response.text == "You chose: opt_a"

            # Get new keyboard message
            await conv.send_message("/inline")
            msg2 = await conv.get_response()

            # Click using the callback_data from button B
            await msg2.click(data=btn_b.data)
            response2 = await conv.get_response()
            assert response2.text == "You chose: opt_b"
    finally:
        await client.disconnect()
