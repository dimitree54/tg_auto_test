"""Behavioral parity tests for core Telethon conversation patterns in serverless mode."""

import pytest
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from tg_auto_test.test_utils.serverless_bot_callback_answer import ServerlessBotCallbackAnswer
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


async def _echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message and update.message.text:
        await update.message.reply_text(update.message.text)


async def _work(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        status = await update.message.reply_text("Loading...")
        await status.edit_text("Done!")


async def _menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("Go", callback_data="go")]])
        await update.message.reply_text("Pick:", reply_markup=kb)


async def _on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.callback_query:
        return
    await update.callback_query.answer()
    if update.callback_query.message:
        await update.callback_query.message.reply_text("Confirmed!")


def _build_parity_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(CommandHandler("work", _work))
    app.add_handler(CommandHandler("menu", _menu))
    app.add_handler(CallbackQueryHandler(_on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _echo))
    return app


@pytest.mark.asyncio
async def test_send_then_response() -> None:
    client = ServerlessTelegramClient(build_application=_build_parity_app)
    await client.connect()
    try:
        async with client.conversation("bot") as conv:
            await conv.send_message("hello")
            msg = await conv.get_response()
            assert msg.text == "hello"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_send_then_response_then_edit() -> None:
    client = ServerlessTelegramClient(build_application=_build_parity_app)
    await client.connect()
    try:
        async with client.conversation("bot") as conv:
            await conv.send_message("/work")
            response = await conv.get_response()
            assert response.text == "Done!"
            edited = await conv.get_edit()
            assert edited.text == "Done!"
            assert edited.id == response.id
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_send_click_then_get_response() -> None:
    client = ServerlessTelegramClient(build_application=_build_parity_app)
    await client.connect()
    try:
        async with client.conversation("bot") as conv:
            await conv.send_message("/menu")
            msg = await conv.get_response()
            assert msg.buttons is not None

            result = await msg.click(data=b"go")
            assert isinstance(result, ServerlessBotCallbackAnswer)

            follow_up = await conv.get_response()
            assert follow_up.text == "Confirmed!"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_outbox_isolation() -> None:
    client = ServerlessTelegramClient(build_application=_build_parity_app)
    await client.connect()
    try:
        async with client.conversation("bot") as conv:
            await conv.send_message("first")
            r1 = await conv.get_response()
            assert r1.text == "first"

            await conv.send_message("second")
            r2 = await conv.get_response()
            assert r2.text == "second"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_get_response_after_edit() -> None:
    client = ServerlessTelegramClient(build_application=_build_parity_app)
    await client.connect()
    try:
        async with client.conversation("bot") as conv:
            await conv.send_message("/work")
            response = await conv.get_response()
            assert response.text == "Done!"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_click_returns_callback_answer_type() -> None:
    client = ServerlessTelegramClient(build_application=_build_parity_app)
    await client.connect()
    try:
        async with client.conversation("bot") as conv:
            await conv.send_message("/menu")
            msg = await conv.get_response()

            result = await msg.click(data=b"go")
            assert isinstance(result, ServerlessBotCallbackAnswer), (
                f"Expected ServerlessBotCallbackAnswer, got {type(result).__name__}"
            )
    finally:
        await client.disconnect()
