"""Unit tests for demo server duck backend (serverless clients)."""

from unittest.mock import AsyncMock, Mock  # noqa: TID251

import pytest

from tg_auto_test.demo_ui.server.backends.duck_backend import DuckBackend
from tg_auto_test.test_utils.models import ServerlessMessage


class TestDuckBackend:
    """Test the duck backend for serverless clients."""

    def test_supports_all_capabilities(self) -> None:
        """Test capability detection for serverless client."""
        mock_client = Mock()
        mock_client.process_callback_query = AsyncMock()
        mock_client.simulate_stars_payment = AsyncMock()
        mock_client.application = Mock()

        backend = DuckBackend(mock_client)

        assert backend.supports_capability("callback_queries")
        assert backend.supports_capability("invoice_payments")
        assert backend.supports_capability("bot_state")
        assert not backend.supports_capability("unknown")

    def test_supports_partial_capabilities(self) -> None:
        """Test capability detection with limited client."""
        mock_client = Mock()
        # Only has callback support, explicitly remove others
        mock_client.process_callback_query = AsyncMock()
        # Remove the payment and application attributes
        if hasattr(mock_client, "simulate_stars_payment"):
            del mock_client.simulate_stars_payment
        if hasattr(mock_client, "application"):
            del mock_client.application

        backend = DuckBackend(mock_client)

        assert backend.supports_capability("callback_queries")
        assert not backend.supports_capability("invoice_payments")
        assert not backend.supports_capability("bot_state")

    @pytest.mark.asyncio
    async def test_handle_callback(self) -> None:
        """Test callback handling."""
        mock_client = Mock()
        mock_response = ServerlessMessage(id=123, text="Button clicked")
        mock_client.process_callback_query = AsyncMock(return_value=mock_response)

        backend = DuckBackend(mock_client)

        result = await backend.handle_callback("test_peer", 456, "button_data")

        mock_client.process_callback_query.assert_called_once_with(456, "button_data")
        assert result is mock_response

    @pytest.mark.asyncio
    async def test_handle_invoice_payment(self) -> None:
        """Test invoice payment handling."""
        mock_client = Mock()
        mock_response = ServerlessMessage(id=789, text="Payment processed")
        mock_client.simulate_stars_payment = AsyncMock()
        mock_client.pop_response = Mock(return_value=mock_response)

        backend = DuckBackend(mock_client)

        result = await backend.handle_invoice_payment(123)

        mock_client.simulate_stars_payment.assert_called_once_with(123)
        mock_client.pop_response.assert_called_once()
        assert result is mock_response

    @pytest.mark.asyncio
    async def test_get_bot_state_success(self) -> None:
        """Test getting bot state from PTB application."""
        mock_client = Mock()
        mock_client.chat_id = 12345

        # Mock PTB structures
        mock_command = Mock()
        mock_command.command = "start"
        mock_command.description = "Start the bot"

        mock_menu_btn = Mock()
        mock_menu_btn.type = "commands"

        mock_bot = Mock()
        mock_bot.get_my_commands = AsyncMock(return_value=[mock_command])
        mock_bot.get_chat_menu_button = AsyncMock(return_value=mock_menu_btn)

        mock_client.application = Mock()
        mock_client.application.bot = mock_bot

        backend = DuckBackend(mock_client)

        commands, menu_type = await backend.get_bot_state()

        assert len(commands) == 1
        assert commands[0] == {"command": "start", "description": "Start the bot"}
        assert menu_type == "commands"

    @pytest.mark.asyncio
    async def test_get_bot_state_fallback(self) -> None:
        """Test bot state fallback when PTB unavailable."""
        # Use spec=[] to avoid automatic Mock attributes
        mock_client = Mock(spec=[])

        backend = DuckBackend(mock_client)

        commands, menu_type = await backend.get_bot_state()

        assert commands == []
        assert menu_type == "default"

    @pytest.mark.asyncio
    async def test_connect_with_lifecycle(self) -> None:
        """Test client connection when managing lifecycle."""
        mock_client = Mock()
        mock_client.connect = AsyncMock()

        backend = DuckBackend(mock_client, manage_lifecycle=True)

        await backend.connect()

        mock_client.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_without_lifecycle(self) -> None:
        """Test client connection when not managing lifecycle."""
        mock_client = Mock()
        mock_client.connect = AsyncMock()

        backend = DuckBackend(mock_client, manage_lifecycle=False)

        await backend.connect()

        mock_client.connect.assert_not_called()
