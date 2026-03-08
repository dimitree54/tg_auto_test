"""Bug #28: set_my_commands in post_init not captured by ServerlessTelegramClient.

When a bot registers commands via set_my_commands in post_init, the
commands are not persisted. GetBotCommandsRequest returns an empty list
because Application.initialize() does NOT invoke post_init — only
run_polling/run_webhook do, and neither is used in serverless mode.

The same issue affects set_chat_menu_button in post_init.
"""

import pytest
from telegram import BotCommand
from telegram.ext import Application, ApplicationBuilder
from telethon.tl.functions.bots import GetBotCommandsRequest, GetBotMenuButtonRequest
from telethon.tl.types import BotCommandScopeDefault, BotMenuButtonCommands, InputUserSelf

from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


async def _post_init_with_commands(application: Application) -> None:
    await application.bot.set_my_commands([
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show help"),
    ])


def _build_app_with_commands(builder: ApplicationBuilder) -> Application:
    return builder.post_init(_post_init_with_commands).build()


@pytest.mark.asyncio
async def test_set_my_commands_in_post_init_visible_via_telethon() -> None:
    """Commands set in post_init must be returned by GetBotCommandsRequest.

    This fails because connect_client only calls Application.initialize(),
    which does NOT invoke post_init. The commands are never registered.
    """
    client = ServerlessTelegramClient(build_application=_build_app_with_commands)
    await client.connect()
    try:
        scope = BotCommandScopeDefault()
        commands = await client(GetBotCommandsRequest(scope=scope, lang_code=""))
        assert len(commands) == 2, f"Expected 2 commands, got {len(commands)}"
        assert commands[0].command == "start"
        assert commands[0].description == "Start the bot"
        assert commands[1].command == "help"
        assert commands[1].description == "Show help"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_set_my_commands_in_post_init_visible_via_ptb() -> None:
    """Commands set in post_init must be returned by bot.get_my_commands.

    Same root cause: post_init is never called in serverless mode.
    """
    client = ServerlessTelegramClient(build_application=_build_app_with_commands)
    await client.connect()
    try:
        bot_state = await client._get_bot_state()
        commands = bot_state["commands"]
        assert len(commands) > 0, f"Expected commands, got empty list: {commands}"
    finally:
        await client.disconnect()


async def _post_init_with_menu_button(application: Application) -> None:
    await application.bot.set_chat_menu_button(menu_button={"type": "commands"})


def _build_app_with_menu_button(builder: ApplicationBuilder) -> Application:
    return builder.post_init(_post_init_with_menu_button).build()


@pytest.mark.asyncio
async def test_set_chat_menu_button_in_post_init() -> None:
    """Menu button set in post_init must be visible via GetBotMenuButtonRequest.

    Same root cause: post_init is never invoked.
    """
    client = ServerlessTelegramClient(build_application=_build_app_with_menu_button)
    await client.connect()
    try:
        user_id = InputUserSelf()
        menu_button = await client(GetBotMenuButtonRequest(user_id=user_id))
        assert isinstance(menu_button, BotMenuButtonCommands), (
            f"Expected BotMenuButtonCommands, got {type(menu_button).__name__}"
        )
    finally:
        await client.disconnect()
