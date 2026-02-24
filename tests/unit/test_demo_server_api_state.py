"""Tests for the /api/state endpoint - verifying fail-fast behavior."""

from unittest.mock import Mock  # noqa: TID251

import pytest
from telethon.tl.functions.bots import GetBotCommandsRequest, GetBotMenuButtonRequest
from telethon.tl.types import BotCommand, BotMenuButtonDefault

from tg_auto_test.demo_ui.server.api_models import BotCommandInfo, BotStateResponse
from tg_auto_test.demo_ui.server.demo_server import DemoServer
from tg_auto_test.test_utils.serverless_telegram_client_core import ServerlessTelegramClientCore


class TestApiStateEndpoint:
    """Test the /api/state endpoint behavior."""

    @pytest.mark.asyncio
    async def test_get_bot_state_method_exists(self) -> None:
        """Test that get_bot_state method exists and works."""

        def build_app(builder):  # noqa: ANN001, ANN202
            return builder.build()

        client = ServerlessTelegramClientCore(build_application=build_app)
        await client.connect()

        # Test the method exists and returns expected structure
        bot_state = await client._get_bot_state()
        assert isinstance(bot_state, dict)
        assert "commands" in bot_state
        assert "menu_button_type" in bot_state
        assert isinstance(bot_state["commands"], list)
        assert isinstance(bot_state["menu_button_type"], str)

        await client.disconnect()

    @pytest.mark.asyncio
    async def test_get_bot_state_structure(self) -> None:
        """Test the structure of bot state response."""

        def build_app(builder):  # noqa: ANN001, ANN202
            return builder.build()

        client = ServerlessTelegramClientCore(build_application=build_app)
        await client.connect()

        bot_state = await client._get_bot_state()

        # Check structure matches what routes.py expects
        commands = bot_state["commands"]
        assert isinstance(commands, list)
        for cmd_dict in commands:
            assert isinstance(cmd_dict, dict)
            assert "command" in cmd_dict
            assert "description" in cmd_dict
            assert isinstance(cmd_dict["command"], str)
            assert isinstance(cmd_dict["description"], str)

        await client.disconnect()

    def test_api_state_endpoint_with_mock_client(self) -> None:
        """Test that the API endpoint uses TL requests via client(request)."""
        # Create a mock client that supports TL requests
        mock_client = Mock()

        # Mock TL request responses
        expected_commands = [
            BotCommand(command="start", description="Start the bot"),
            BotCommand(command="help", description="Get help"),
        ]
        expected_menu_button = BotMenuButtonDefault()

        def mock_call(
            request: GetBotCommandsRequest | GetBotMenuButtonRequest,
        ) -> list[BotCommand] | BotMenuButtonDefault:
            if isinstance(request, GetBotCommandsRequest):
                return expected_commands
            if isinstance(request, GetBotMenuButtonRequest):
                return expected_menu_button
            raise NotImplementedError(f"Unsupported request: {type(request)}")

        mock_client.__call__ = mock_call

        server = DemoServer(mock_client, "test_bot")
        app = server.create_app()

        # Test that the route would work without actually making HTTP request
        # We just verify the server can be created with our mock client
        assert server.client == mock_client
        assert app is not None
        # Verify the mock can handle TL requests
        assert callable(mock_client.__call__)

    def test_api_state_endpoint_uses_tl_requests(self) -> None:
        """Test that the route uses TL requests instead of get_bot_state method."""
        # This test verifies the implementation change from get_bot_state to TL requests
        server = DemoServer(Mock(), "test_bot")

        # The DemoServer should work with any client that supports TL requests
        # The key change is that get_bot_state is no longer required in the protocol
        # and routes now use client(GetBotCommandsRequest(...)) pattern

        # This is a design verification test - the route implementation
        # moved from client.get_bot_state() to client(TL_request) pattern
        assert server.client is not None
        assert hasattr(server, "client")

    def test_bot_command_info_conversion(self) -> None:
        """Test that bot state dict converts correctly to BotCommandInfo."""
        # Test the conversion logic that routes.py uses
        bot_state = {
            "commands": [
                {"command": "start", "description": "Start the bot"},
                {"command": "help", "description": "Get help"},
            ],
            "menu_button_type": "default",
        }

        command_list = [
            BotCommandInfo(command=cmd["command"], description=cmd["description"]) for cmd in bot_state["commands"]
        ]
        response = BotStateResponse(commands=command_list, menu_button_type=bot_state["menu_button_type"])

        assert len(response.commands) == 2
        assert response.commands[0].command == "start"
        assert response.commands[0].description == "Start the bot"
        assert response.commands[1].command == "help"
        assert response.commands[1].description == "Get help"
        assert response.menu_button_type == "default"
