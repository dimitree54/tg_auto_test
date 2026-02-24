"""Test poll handling with ServerlessTelegramClient."""

import pytest
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes

from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


async def _poll_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /poll command and send a poll."""
    del context  # Unused but required by handler signature
    if update.message:
        await update.message.reply_poll(
            question="What's your favorite color?",
            options=["Red", "Green", "Blue"],
            is_anonymous=False,
        )


def build_poll_application(builder: ApplicationBuilder) -> Application:
    """Build a test application with poll handler."""
    app = builder.build()
    app.add_handler(CommandHandler("poll", _poll_handler))
    return app


@pytest.mark.asyncio
async def test_send_poll() -> None:
    """Test sending a poll and receiving it back."""
    client = ServerlessTelegramClient(build_application=build_poll_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/poll")
            msg = await conv.get_response()

            # Basic message properties
            assert isinstance(msg.id, int)
            assert msg.id > 0
            assert msg.text == ""  # polls are not text

            # Poll-specific properties
            assert msg.poll is not None
            poll = msg.poll
            assert poll.poll.question.text == "What's your favorite color?"
            assert len(poll.poll.answers) == 3
            assert poll.poll.answers[0].text.text == "Red"
            assert poll.poll.answers[1].text.text == "Green"
            assert poll.poll.answers[2].text.text == "Blue"
            assert poll.poll.public_voters  # not anonymous

    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_poll_api_call_structure() -> None:
    """Test that sendPoll API call is captured correctly."""
    client = ServerlessTelegramClient(build_application=build_poll_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/poll")
            await conv.get_response()

            # Check API calls
            api_calls = client._api_calls  # noqa: SLF001
            send_poll_calls = [call for call in api_calls if call.api_method == "sendPoll"]
            assert len(send_poll_calls) == 1

            call = send_poll_calls[0]
            assert call.parameters["question"] == "What's your favorite color?"
            assert "options" in call.parameters

            # Check that result contains poll data
            assert call.result is not None and isinstance(call.result, dict) and "poll" in call.result
            poll_data = call.result["poll"]
            assert isinstance(poll_data, dict) and poll_data["question"] == "What's your favorite color?"
            options = poll_data["options"]
            assert isinstance(options, list) and len(options) == 3 and isinstance(options[0], dict)
            assert options[0]["text"] == "Red"

    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_multiple_polls() -> None:
    """Test that multiple polls get unique IDs."""
    client = ServerlessTelegramClient(build_application=build_poll_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/poll")
            msg1 = await conv.get_response()

            await conv.send_message("/poll")
            msg2 = await conv.get_response()

            # Both should have polls but with different IDs
            assert msg1.poll is not None
            assert msg2.poll is not None
            assert msg1.poll.poll.id != msg2.poll.poll.id

            # Check that API calls have different poll IDs
            api_calls = client._api_calls  # noqa: SLF001
            send_poll_calls = [call for call in api_calls if call.api_method == "sendPoll"]
            assert len(send_poll_calls) == 2

            assert send_poll_calls[0].result is not None and isinstance(send_poll_calls[0].result, dict)
            assert send_poll_calls[1].result is not None and isinstance(send_poll_calls[1].result, dict)

            poll1_data = send_poll_calls[0].result["poll"]
            poll2_data = send_poll_calls[1].result["poll"]
            assert isinstance(poll1_data, dict) and isinstance(poll2_data, dict)
            assert poll1_data["id"] != poll2_data["id"]

    finally:
        await client.disconnect()
