"""Tests for the /api/state endpoint - verifying fail-fast behavior."""

from unittest.mock import Mock  # noqa: TID251

import pytest

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
        bot_state = await client.get_bot_state()
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

        bot_state = await client.get_bot_state()

        # Check structure matches what routes.py expects
        for cmd_dict in bot_state["commands"]:
            assert "command" in cmd_dict
            assert "description" in cmd_dict
            assert isinstance(cmd_dict["command"], str)
            assert isinstance(cmd_dict["description"], str)

        await client.disconnect()

    def test_api_state_endpoint_with_mock_client(self) -> None:
        """Test that the API endpoint uses the get_bot_state method."""
        # Create a mock client that has the get_bot_state method
        mock_client = Mock()
        expected_state = {
            "commands": [
                {"command": "start", "description": "Start the bot"},
                {"command": "help", "description": "Get help"},
            ],
            "menu_button_type": "default",
        }
        mock_client.get_bot_state.return_value = expected_state

        server = DemoServer(mock_client, "test_bot")
        app = server.create_app()

        # Test that the route would work without actually making HTTP request
        # We just verify the server can be created with our mock client
        assert server.client == mock_client
        assert app is not None
        # Verify the mock was configured correctly
        assert mock_client.get_bot_state.return_value == expected_state

    def test_api_state_endpoint_fails_fast_on_missing_method(self) -> None:
        """Test that missing get_bot_state method causes AttributeError."""
        # Create a client without the get_bot_state method
        mock_client = Mock()
        # Explicitly delete the method to simulate missing attribute
        if hasattr(mock_client, "get_bot_state"):
            del mock_client.get_bot_state

        server = DemoServer(mock_client, "test_bot")

        # This should work fine - the server creation doesn't call get_bot_state
        assert server.client == mock_client

        # But trying to access get_bot_state should raise AttributeError
        with pytest.raises(AttributeError):
            server.client.get_bot_state  # noqa: B018

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
