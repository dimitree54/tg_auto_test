"""Test Telethon SetBotMenuButtonRequest handler."""

import pytest
from telethon.tl import functions, types

from tests.unit.helpers_ptb_app import build_test_application
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient

MenuButton = types.BotMenuButtonDefault | types.BotMenuButtonCommands | types.BotMenuButton
MenuButtonType = type[types.BotMenuButtonDefault] | type[types.BotMenuButtonCommands] | type[types.BotMenuButton]


async def _set_menu_button(client: ServerlessTelegramClient, button: MenuButton) -> None:
    request = functions.bots.SetBotMenuButtonRequest(user_id=types.InputUserSelf(), button=button)
    result = await client(request)
    assert result is True


async def _get_menu_button(client: ServerlessTelegramClient) -> MenuButton:
    request = functions.bots.GetBotMenuButtonRequest(user_id=types.InputUserSelf())
    result = await client(request)
    if isinstance(result, (types.BotMenuButtonDefault, types.BotMenuButtonCommands, types.BotMenuButton)):
        return result
    raise TypeError(f"Expected bot menu button, got {type(result).__name__}")


async def _assert_menu_button(client: ServerlessTelegramClient, expected_type: MenuButtonType) -> None:
    menu_button = await _get_menu_button(client)
    assert isinstance(menu_button, expected_type)


async def _set_and_assert_menu_button(
    client: ServerlessTelegramClient,
    button: MenuButton,
    expected_type: MenuButtonType,
) -> None:
    await _set_menu_button(client, button)
    await _assert_menu_button(client, expected_type)


@pytest.mark.asyncio
async def test_set_bot_menu_button_default() -> None:
    """Test SetBotMenuButtonRequest with BotMenuButtonDefault."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        await _set_and_assert_menu_button(client, types.BotMenuButtonCommands(), types.BotMenuButtonCommands)
        await _set_and_assert_menu_button(client, types.BotMenuButtonDefault(), types.BotMenuButtonDefault)
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_set_bot_menu_button_commands() -> None:
    """Test SetBotMenuButtonRequest with BotMenuButtonCommands."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        await _set_and_assert_menu_button(client, types.BotMenuButtonCommands(), types.BotMenuButtonCommands)
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_set_bot_menu_button_url_resets_to_default() -> None:
    """Test unsupported URL menu buttons reset to default."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        await _set_and_assert_menu_button(client, types.BotMenuButtonCommands(), types.BotMenuButtonCommands)
        await _set_and_assert_menu_button(
            client,
            types.BotMenuButton(text="Open", url="https://example.test"),
            types.BotMenuButtonDefault,
        )

    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_set_bot_menu_button_multiple_changes() -> None:
    """Test multiple menu button changes work correctly."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        await _assert_menu_button(client, types.BotMenuButtonDefault)

        commands_button = types.BotMenuButtonCommands()
        await _set_and_assert_menu_button(client, commands_button, types.BotMenuButtonCommands)
        await _set_and_assert_menu_button(client, types.BotMenuButtonDefault(), types.BotMenuButtonDefault)
        await _set_and_assert_menu_button(client, commands_button, types.BotMenuButtonCommands)

    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_integration_reset_commands_and_set_menu_button() -> None:
    """Test integration of reset commands and set menu button together."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        # Set up initial state with commands and menu button
        scope = types.BotCommandScopeDefault()
        commands = [
            types.BotCommand(command="start", description="Start"),
            types.BotCommand(command="help", description="Help"),
        ]
        set_commands_request = functions.bots.SetBotCommandsRequest(scope=scope, commands=commands, lang_code="en")
        await client(set_commands_request)

        await _set_menu_button(client, types.BotMenuButtonCommands())

        # Verify initial state
        get_commands_request = functions.bots.GetBotCommandsRequest(scope=scope, lang_code="en")
        stored_commands = await client(get_commands_request)
        assert len(stored_commands) == 2

        await _assert_menu_button(client, types.BotMenuButtonCommands)

        # Reset commands
        reset_commands_request = functions.bots.ResetBotCommandsRequest(scope=scope, lang_code="en")
        result = await client(reset_commands_request)
        assert result is True

        # Set menu to default
        await _set_menu_button(client, types.BotMenuButtonDefault())

        # Verify final state
        stored_commands = await client(get_commands_request)
        assert len(stored_commands) == 0

        await _assert_menu_button(client, types.BotMenuButtonDefault)

    finally:
        await client.disconnect()
