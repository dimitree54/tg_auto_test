"""Reproduce GitHub issue #30: conversation helpers do not wait for async output."""

import asyncio

import pytest
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters

from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient

_DELAY_SECONDS = 0.05


async def _status_then_follow_up_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.message:
        return
    await update.message.reply_text("Working...")

    async def _send_follow_up() -> None:
        await asyncio.sleep(_DELAY_SECONDS)
        await update.message.reply_text("Done!")

    asyncio.create_task(_send_follow_up())


def _build_follow_up_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _status_then_follow_up_handler))
    return app


async def _status_then_edit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.message:
        return
    status = await update.message.reply_text("Working...")

    async def _edit_later() -> None:
        await asyncio.sleep(_DELAY_SECONDS)
        await status.edit_text("Done!")

    asyncio.create_task(_edit_later())


def _build_edit_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _status_then_edit_handler))
    return app


@pytest.mark.asyncio
async def test_get_response_waits_for_delayed_follow_up() -> None:
    client = ServerlessTelegramClient(build_application=_build_follow_up_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("hello")
            status = await conv.get_response()
            assert status.text == "Working..."
            follow_up = await conv.get_response()
            assert follow_up.text == "Done!"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_get_edit_waits_for_delayed_edit() -> None:
    client = ServerlessTelegramClient(build_application=_build_edit_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("hello")
            status = await conv.get_response()
            assert status.text == "Working..."
            edited = await conv.get_edit()
            assert edited.id == status.id
            assert edited.text == "Done!"
    finally:
        await client.disconnect()
