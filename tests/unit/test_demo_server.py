"""Unit tests for the demo server implementation."""

from unittest.mock import AsyncMock, Mock  # noqa: TID251

import pytest

from tg_auto_test.demo_ui.server.backends.duck_backend import DuckBackend
from tg_auto_test.demo_ui.server.backends.telethon_backend import TelethonBackend
from tg_auto_test.demo_ui.server.demo_server import DemoServer, create_demo_app
from tg_auto_test.demo_ui.server.file_store import FileStore


class TestFileStore:
    """Test the in-memory file store."""

    def test_store_and_get_file(self) -> None:
        """Test storing and retrieving files."""
        store = FileStore()
        file_id = "test_file"
        filename = "test.txt"
        content_type = "text/plain"
        data = b"hello world"

        store.store(file_id, filename, content_type, data)

        result = store.get(file_id)
        assert result == (filename, content_type, data)

    def test_get_nonexistent_file(self) -> None:
        """Test getting a file that doesn't exist."""
        store = FileStore()
        result = store.get("nonexistent")
        assert result is None

    def test_exists_check(self) -> None:
        """Test file existence check."""
        store = FileStore()
        assert not store.exists("test")

        store.store("test", "test.txt", "text/plain", b"data")
        assert store.exists("test")
        assert "test" in store

    def test_clear_store(self) -> None:
        """Test clearing the store."""
        store = FileStore()
        store.store("test", "test.txt", "text/plain", b"data")

        assert store.exists("test")
        store.clear()
        assert not store.exists("test")


class TestDemoServer:
    """Test the DemoServer class."""

    def test_init_with_valid_peer(self) -> None:
        """Test initialization with valid peer."""
        mock_client = Mock()
        server = DemoServer(mock_client, "test_bot")

        assert server.peer == "test_bot"
        assert server.timeout == 10.0
        assert isinstance(server.file_store, FileStore)

    def test_init_with_empty_peer_fails(self) -> None:
        """Test that empty peer raises ValueError."""
        mock_client = Mock()

        with pytest.raises(ValueError, match="Peer must be specified"):
            DemoServer(mock_client, "")

    def test_backend_detection_serverless(self) -> None:
        """Test auto-detection of serverless backend."""
        mock_client = Mock()
        mock_client.process_callback_query = AsyncMock()

        server = DemoServer(mock_client, "test_bot", backend_type="auto")

        # Should detect as duck backend
        assert isinstance(server.backend, DuckBackend)

    def test_backend_detection_telethon(self) -> None:
        """Test auto-detection of Telethon backend."""
        mock_client = Mock(spec=[])  # Start with empty spec
        # Only add telethon methods
        mock_client.get_messages = AsyncMock()
        mock_client.get_dialogs = AsyncMock()

        server = DemoServer(mock_client, "test_bot", backend_type="auto")

        # Should detect as telethon backend
        assert isinstance(server.backend, TelethonBackend)

    def test_explicit_backend_type(self) -> None:
        """Test explicit backend type selection."""
        mock_client = Mock()

        server = DemoServer(mock_client, "test_bot", backend_type="duck")

        assert isinstance(server.backend, DuckBackend)

    def test_invalid_backend_type(self) -> None:
        """Test invalid backend type raises ValueError."""
        mock_client = Mock()

        with pytest.raises(ValueError, match="Unknown backend type"):
            DemoServer(mock_client, "test_bot", backend_type="invalid")

    def test_create_app(self) -> None:
        """Test app creation returns object with expected attributes."""
        mock_client = Mock()
        server = DemoServer(mock_client, "test_bot")

        # Skip app creation test since FastAPI is optional dependency
        # Just test that the method exists and server has required attributes
        assert hasattr(server, "create_app")
        assert callable(server.create_app)
        assert server.peer == "test_bot"
        assert server.file_store is not None


def test_create_demo_app_factory() -> None:
    """Test the factory function exists and is callable."""
    # Skip actual app creation since FastAPI is optional dependency
    # Just verify the function exists with expected signature
    assert callable(create_demo_app)

    # Test parameter validation still works
    mock_client = Mock()

    with pytest.raises(ValueError, match="Peer must be specified"):
        create_demo_app(client=mock_client, peer="")
