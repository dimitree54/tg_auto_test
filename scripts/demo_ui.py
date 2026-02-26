"""Demo UI: simple echo bot with the tg-auto-test demo server."""

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters

from tg_auto_test.demo_ui.server.demo_server import create_demo_app
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


async def echo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message and update.message.text:
        await update.message.reply_text(f"Echo: {update.message.text}")


def build_echo_application(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(MessageHandler(filters.TEXT, echo_handler))
    return app


_client = ServerlessTelegramClient(build_application=build_echo_application)

app = create_demo_app(client=_client, peer="echo_bot")
