"""Test text message handling with ServerlessTelegramClient."""

import pytest

from tests.unit.helpers_ptb_app import build_test_application
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


@pytest.mark.asyncio
async def test_echo_text_message() -> None:
    """Test that text messages are echoed back correctly."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("hello")
            msg = await conv.get_response()
            assert msg.text == "hello"
            assert isinstance(msg.id, int)
            assert msg.id > 0
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_start_command() -> None:
    """Test /start command response."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/start")
            msg = await conv.get_response()
            assert msg.text == "Welcome!"
            assert isinstance(msg.id, int)
            assert msg.id > 0
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_message_id_increments() -> None:
    """Test that message IDs increment for subsequent messages."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("first")
            msg1 = await conv.get_response()

            await conv.send_message("second")
            msg2 = await conv.get_response()

            assert msg2.id > msg1.id
            assert msg1.text == "first"
            assert msg2.text == "second"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_multiple_text_messages() -> None:
    """Test sending multiple text messages in sequence."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            test_messages = ["hello world", "testing 123", "final message"]

            for text in test_messages:
                await conv.send_message(text)
                msg = await conv.get_response()
                assert msg.text == text
                assert isinstance(msg.id, int)
                assert msg.id > 0
    finally:
        await client.disconnect()
