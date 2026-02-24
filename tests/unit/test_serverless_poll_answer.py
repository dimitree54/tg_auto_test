"""Test poll answer handling with ServerlessTelegramClient using Telethon API."""

import pytest
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes, PollAnswerHandler
from telethon.tl.functions.messages import SendVoteRequest
from telethon.tl.types import InputPeerEmpty

from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


async def _poll_answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle poll answer and respond based on the selected option."""
    if update.poll_answer:
        poll_answer = update.poll_answer
        poll_id = poll_answer.poll_id
        option_ids = poll_answer.option_ids
        user_name = poll_answer.user.first_name if poll_answer.user else "Unknown"

        # Get poll data stored during poll creation
        poll_data = context.bot_data.get(poll_id)
        if not poll_data:
            user_id = poll_answer.user.id if poll_answer.user else 0
            await context.bot.send_message(chat_id=user_id, text=f"Poll {poll_id} not found in bot data.")
            return

        options = poll_data["options"]
        selected_options = [options[i] for i in option_ids if i < len(options)]

        response_text = f"{user_name} voted for: {', '.join(selected_options)}"
        user_id = poll_answer.user.id if poll_answer.user else 0
        await context.bot.send_message(chat_id=user_id, text=response_text)


async def _poll_with_storage_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /poll command, store poll data, and send a poll."""
    if update.message:
        poll_msg = await update.message.reply_poll(
            question="What's your favorite color?",
            options=["Red", "Green", "Blue"],
            is_anonymous=False,
        )
        # Store poll data for later retrieval
        if poll_msg.poll:
            # Use the original Poll ID string
            poll_id = poll_msg.poll.id
            context.bot_data[poll_id] = {"options": ["Red", "Green", "Blue"], "question": "What's your favorite color?"}


def build_poll_with_answer_application(builder: ApplicationBuilder) -> Application:
    """Build a test application with poll and poll answer handlers."""
    app = builder.build()
    app.add_handler(CommandHandler("poll", _poll_with_storage_handler))
    app.add_handler(PollAnswerHandler(_poll_answer_handler))
    return app


async def _setup_poll_and_get_message(client: ServerlessTelegramClient) -> tuple[int, bytes]:
    """Setup poll and return message_id and first option bytes."""
    async with client.conversation("test_bot") as conv:
        await conv.send_message("/poll")
        poll_msg = await conv.get_response()
        assert poll_msg.poll is not None
        # Return message ID and first option bytes
        first_option_bytes = poll_msg.poll.poll.answers[0].option
        return poll_msg.id, first_option_bytes


@pytest.mark.asyncio
async def test_send_vote_request() -> None:
    """Test poll answer processing end-to-end using SendVoteRequest."""
    client = ServerlessTelegramClient(build_application=build_poll_with_answer_application)
    await client.connect()
    try:
        message_id, first_option_bytes = await _setup_poll_and_get_message(client)

        # Use Telethon SendVoteRequest
        vote_request = SendVoteRequest(peer=InputPeerEmpty(), msg_id=message_id, options=[first_option_bytes])
        await client(vote_request)

        # Get the response
        response = client._pop_response()  # noqa: SLF001
        assert response.text == "Alice voted for: Red"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_send_vote_request_multiple_options() -> None:
    """Test poll answer with multiple options using SendVoteRequest."""
    client = ServerlessTelegramClient(build_application=build_poll_with_answer_application)
    await client.connect()
    try:
        message_id, _ = await _setup_poll_and_get_message(client)

        # Use bytes for options 0 and 2 (Red and Blue)
        option_bytes = [bytes([0]), bytes([2])]

        vote_request = SendVoteRequest(peer=InputPeerEmpty(), msg_id=message_id, options=option_bytes)
        await client(vote_request)

        response = client._pop_response()  # noqa: SLF001
        assert response.text == "Alice voted for: Red, Blue"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_send_vote_request_unknown_poll() -> None:
    """Test poll answer for unknown poll message ID."""
    client = ServerlessTelegramClient(build_application=build_poll_with_answer_application)
    await client.connect()
    try:
        # Use SendVoteRequest for non-existent message
        vote_request = SendVoteRequest(
            peer=InputPeerEmpty(),
            msg_id=99999,  # Non-existent message ID
            options=[bytes([0])],
        )

        # Should raise RuntimeError for unknown poll
        with pytest.raises(RuntimeError, match="Poll not found for message_id 99999"):
            await client(vote_request)

    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_send_vote_request_api_call_structure() -> None:
    """Test that SendVoteRequest generates correct API calls."""
    client = ServerlessTelegramClient(build_application=build_poll_with_answer_application)
    await client.connect()
    try:
        message_id, _ = await _setup_poll_and_get_message(client)
        client.request.calls.clear()  # Clear previous API calls to focus on poll answer

        # Vote for option 1 (Green)
        vote_request = SendVoteRequest(peer=InputPeerEmpty(), msg_id=message_id, options=[bytes([1])])
        await client(vote_request)

        # Check that sendMessage was called as a result
        send_message_calls = [call for call in client.api_calls if call.api_method == "sendMessage"]
        assert len(send_message_calls) == 1
        call = send_message_calls[0]
        assert str(call.parameters["chat_id"]) == str(client.user_id)
        assert "voted for: Green" in str(call.parameters["text"])
    finally:
        await client.disconnect()
