"""Test Telethon ResetBotCommandsRequest handler."""

import pytest
from telethon.tl import functions, types

from tests.unit.helpers_ptb_app import build_test_application
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


async def _test_reset_commands_for_scope(
    client: ServerlessTelegramClient, scope: types.TypeBotCommandScope, command_name: str = "start"
) -> None:
    """Helper to test reset commands for a given scope."""
    # Set some commands
    commands = [types.BotCommand(command=command_name, description="Test command")]
    set_request = functions.bots.SetBotCommandsRequest(scope=scope, commands=commands, lang_code="en")
    result = await client(set_request)
    assert result is True

    # Verify commands are set
    get_request = functions.bots.GetBotCommandsRequest(scope=scope, lang_code="en")
    stored_commands = await client(get_request)
    assert len(stored_commands) == 1
    assert stored_commands[0].command == command_name

    # Reset the commands
    reset_request = functions.bots.ResetBotCommandsRequest(scope=scope, lang_code="en")
    result = await client(reset_request)
    assert result is True

    # Verify commands are cleared
    stored_commands = await client(get_request)
    assert len(stored_commands) == 0


@pytest.mark.asyncio
async def test_reset_bot_commands_request() -> None:
    """Test ResetBotCommandsRequest clears commands for the given scope."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        scope = types.BotCommandScopeDefault()
        await _test_reset_commands_for_scope(client, scope)
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_reset_bot_commands_request_peer_scope() -> None:
    """Test ResetBotCommandsRequest with BotCommandScopePeer."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        peer = types.InputPeerUser(user_id=123456, access_hash=0)
        scope = types.BotCommandScopePeer(peer=peer)
        await _test_reset_commands_for_scope(client, scope, "help")
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_reset_bot_commands_different_scopes() -> None:
    """Test that resetting commands only affects the specified scope."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        # Set commands for default scope
        default_scope = types.BotCommandScopeDefault()
        default_commands = [types.BotCommand(command="start", description="Start the bot")]
        set_default_request = functions.bots.SetBotCommandsRequest(
            scope=default_scope, commands=default_commands, lang_code="en"
        )
        await client(set_default_request)

        # Set commands for peer scope
        peer = types.InputPeerUser(user_id=123456, access_hash=0)
        peer_scope = types.BotCommandScopePeer(peer=peer)
        peer_commands = [types.BotCommand(command="help", description="Show help")]
        set_peer_request = functions.bots.SetBotCommandsRequest(
            scope=peer_scope, commands=peer_commands, lang_code="en"
        )
        await client(set_peer_request)

        # Verify both are set
        get_default_request = functions.bots.GetBotCommandsRequest(scope=default_scope, lang_code="en")
        get_peer_request = functions.bots.GetBotCommandsRequest(scope=peer_scope, lang_code="en")

        default_stored = await client(get_default_request)
        peer_stored = await client(get_peer_request)
        assert len(default_stored) == 1
        assert len(peer_stored) == 1

        # Reset only the peer scope commands
        reset_peer_request = functions.bots.ResetBotCommandsRequest(scope=peer_scope, lang_code="en")
        result = await client(reset_peer_request)
        assert result is True

        # Verify peer commands are cleared but default commands remain
        default_stored = await client(get_default_request)
        peer_stored = await client(get_peer_request)
        assert len(default_stored) == 1  # Should still be there
        assert len(peer_stored) == 0  # Should be cleared

    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_reset_bot_commands_nonexistent_scope() -> None:
    """Test that resetting nonexistent scope doesn't raise error."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        # Try to reset commands for a scope that has no commands set
        scope = types.BotCommandScopeDefault()
        reset_request = functions.bots.ResetBotCommandsRequest(scope=scope, lang_code="en")
        result = await client(reset_request)
        assert result is True  # Should succeed even if nothing to reset

        # Verify no commands exist
        get_request = functions.bots.GetBotCommandsRequest(scope=scope, lang_code="en")
        stored_commands = await client(get_request)
        assert len(stored_commands) == 0

    finally:
        await client.disconnect()
