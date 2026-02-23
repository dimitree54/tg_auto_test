"""Test poll answer handling with ServerlessTelegramClient."""

import pytest
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes, PollAnswerHandler

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


async def _setup_poll_and_get_id(client: ServerlessTelegramClient) -> str:
    """Setup poll and return poll_id."""
    async with client.conversation("test_bot") as conv:
        await conv.send_message("/poll")
        poll_msg = await conv.get_response()
        assert poll_msg.poll is not None
        # Get the original string poll ID from the poll_data (before hashing)
        if poll_msg.poll_data and isinstance(poll_msg.poll_data, dict):
            poll_id = str(poll_msg.poll_data.get("id", ""))
        else:
            poll_id = str(poll_msg.poll.poll.id)  # Fallback to hashed version
        return poll_id


@pytest.mark.asyncio
async def test_process_poll_answer() -> None:
    """Test poll answer processing end-to-end."""
    client = ServerlessTelegramClient(build_application=build_poll_with_answer_application)
    await client.connect()
    try:
        poll_id = await _setup_poll_and_get_id(client)
        response = await client.process_poll_answer(poll_id, [0])
        assert response.text == "Alice voted for: Red"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_process_poll_answer_multiple_options() -> None:
    """Test poll answer with multiple options selected."""
    client = ServerlessTelegramClient(build_application=build_poll_with_answer_application)
    await client.connect()
    try:
        poll_id = await _setup_poll_and_get_id(client)
        response = await client.process_poll_answer(poll_id, [0, 2])
        assert response.text == "Alice voted for: Red, Blue"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_process_poll_answer_unknown_poll() -> None:
    """Test poll answer for unknown poll ID."""
    client = ServerlessTelegramClient(build_application=build_poll_with_answer_application)
    await client.connect()
    try:
        # Process poll answer for non-existent poll
        response = await client.process_poll_answer("unknown_poll_123", [0])

        # Should get error message about poll not found
        assert "Poll unknown_poll_123 not found in bot data." in response.text

    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_process_poll_answer_api_call_structure() -> None:
    """Test that poll answer generates correct API calls."""
    client = ServerlessTelegramClient(build_application=build_poll_with_answer_application)
    await client.connect()
    try:
        poll_id = await _setup_poll_and_get_id(client)
        client.request.calls.clear()  # Clear previous API calls to focus on poll answer
        await client.process_poll_answer(poll_id, [1])

        # Check that sendMessage was called as a result
        send_message_calls = [call for call in client.api_calls if call.api_method == "sendMessage"]
        assert len(send_message_calls) == 1
        call = send_message_calls[0]
        assert str(call.parameters["chat_id"]) == str(client.user_id)
        assert "voted for: Green" in str(call.parameters["text"])
    finally:
        await client.disconnect()
