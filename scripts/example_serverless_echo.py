"""Example script demonstrating ServerlessTelegramClient usage.

This script shows how to:
1. Define a simple echo bot using python-telegram-bot
2. Wire it into ServerlessTelegramClient
3. Interact with the bot without real Telegram network access

Run: uv run python scripts/example_serverless_echo.py
"""

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters

from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


async def echo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Simple echo handler that repeats back the user's message."""
    del context  # Unused but required by handler signature
    if update.message and update.message.text:
        await update.message.reply_text(f"Echo: {update.message.text}")


def build_echo_application(builder: ApplicationBuilder) -> Application:
    """Build a simple echo bot application.

    Args:
        builder: Pre-configured ApplicationBuilder from ServerlessTelegramClient

    Returns:
        Application with echo handler
    """
    app = builder.build()
    app.add_handler(MessageHandler(filters.TEXT, echo_handler))
    return app


async def main() -> None:
    """Demonstrate serverless bot interaction."""
    print("🤖 Starting serverless Telegram bot demo...")

    # Create serverless client with our echo bot
    client = ServerlessTelegramClient(build_application=build_echo_application)

    # Connect and interact
    await client.connect()
    try:
        async with client.conversation("echo_bot") as conv:
            # Send a message
            print("📤 Sending: 'Hello, bot!'")
            await conv.send_message("Hello, bot!")

            # Get response
            response = await conv.get_response()
            print(f"📥 Received: '{response.text}'")

            # Send another message
            print("📤 Sending: 'How are you?'")
            await conv.send_message("How are you?")

            # Get response
            response2 = await conv.get_response()
            print(f"📥 Received: '{response2.text}'")

    finally:
        await client.disconnect()

    print("✅ Demo complete!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
