"""Unit tests for demo server Telethon backend."""

from unittest.mock import AsyncMock, Mock  # noqa: TID251

import pytest

from tg_auto_test.demo_ui.server.backends.telethon_backend import TelethonBackend


class TestTelethonBackend:
    """Test the Telethon backend for real clients."""

    def test_supports_limited_capabilities(self) -> None:
        """Test capability detection for Telethon client."""
        mock_client = Mock()
        backend = TelethonBackend(mock_client)

        assert backend.supports_capability("callback_queries")
        assert not backend.supports_capability("invoice_payments")
        assert not backend.supports_capability("bot_state")
        assert not backend.supports_capability("unknown")

    @pytest.mark.asyncio
    async def test_handle_callback(self) -> None:
        """Test callback handling via Telethon."""
        mock_client = Mock()
        mock_message = Mock()
        mock_message.click = AsyncMock()
        mock_client.get_messages = AsyncMock(return_value=mock_message)

        backend = TelethonBackend(mock_client)

        result = await backend.handle_callback("test_peer", 456, "button_data")

        mock_client.get_messages.assert_called_once_with("test_peer", ids=456)
        mock_message.click.assert_called_once_with(data=b"button_data")
        assert result.text == "Callback processed"

    @pytest.mark.asyncio
    async def test_handle_callback_message_not_found(self) -> None:
        """Test callback handling when message not found."""
        mock_client = Mock()
        mock_client.get_messages = AsyncMock(return_value=None)

        backend = TelethonBackend(mock_client)

        with pytest.raises(RuntimeError, match="Message 456 not found"):
            await backend.handle_callback("test_peer", 456, "button_data")

    @pytest.mark.asyncio
    async def test_handle_invoice_payment_not_supported(self) -> None:
        """Test that invoice payments raise error in Telethon backend."""
        mock_client = Mock()
        backend = TelethonBackend(mock_client)

        with pytest.raises(RuntimeError, match="Invoice payments not supported"):
            await backend.handle_invoice_payment(123)

    @pytest.mark.asyncio
    async def test_get_bot_state_returns_default(self) -> None:
        """Test that bot state returns default values."""
        mock_client = Mock()
        backend = TelethonBackend(mock_client)

        commands, menu_type = await backend.get_bot_state()

        assert commands == []
        assert menu_type == "default"

    @pytest.mark.asyncio
    async def test_disconnect_with_lifecycle(self) -> None:
        """Test client disconnection when managing lifecycle."""
        mock_client = Mock()
        mock_client.disconnect = AsyncMock()

        backend = TelethonBackend(mock_client, manage_lifecycle=True)

        await backend.disconnect()

        mock_client.disconnect.assert_called_once()
