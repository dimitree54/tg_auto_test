"""Integration tests for the demo server."""

from unittest.mock import AsyncMock, Mock  # noqa: TID251

from tg_auto_test.demo_ui.server.backends.duck_backend import DuckBackend
from tg_auto_test.demo_ui.server.backends.telethon_backend import TelethonBackend
from tg_auto_test.demo_ui.server.demo_server import DemoServer
from tg_auto_test.demo_ui.server.file_store import FileStore


def test_demo_server_backend_detection() -> None:
    """Test demo server backend detection with mock clients."""
    # Test serverless client detection
    mock_serverless = Mock()
    mock_serverless.process_callback_query = AsyncMock()

    server_duck = DemoServer(mock_serverless, "test_bot", backend_type="auto")

    assert isinstance(server_duck.backend, DuckBackend)

    # Test capability detection
    assert server_duck.backend.supports_capability("callback_queries")

    # Test Telethon client detection
    mock_telethon = Mock()
    mock_telethon.get_messages = AsyncMock()
    mock_telethon.get_dialogs = AsyncMock()
    # Ensure no serverless methods exist
    if hasattr(mock_telethon, "process_callback_query"):
        del mock_telethon.process_callback_query
    if hasattr(mock_telethon, "conversation"):
        del mock_telethon.conversation

    server_telethon = DemoServer(mock_telethon, "test_bot", backend_type="auto")

    assert isinstance(server_telethon.backend, TelethonBackend)


def test_demo_server_file_handling() -> None:
    """Test file storage and retrieval."""

    file_store = FileStore()

    # Store a test file
    test_data = b"hello world"
    file_id = "test_123"
    file_store.store(file_id, "test.txt", "text/plain", test_data)

    # Retrieve and verify
    result = file_store.get(file_id)
    assert result is not None
    filename, content_type, data = result
    assert filename == "test.txt"
    assert content_type == "text/plain"
    assert data == test_data

    # Test existence checks
    assert file_store.exists(file_id)
    assert file_id in file_store
    assert not file_store.exists("nonexistent")

    # Test clearing
    file_store.clear()
    assert not file_store.exists(file_id)
