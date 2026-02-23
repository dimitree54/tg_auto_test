"""Integration tests for the demo server."""

from unittest.mock import Mock  # noqa: TID251

from tg_auto_test.demo_ui.server.demo_server import DemoServer
from tg_auto_test.demo_ui.server.file_store import FileStore


def test_demo_server_telethon_interface() -> None:
    """Test demo server with Telethon-compatible client."""
    # Test with mock client that has Telethon methods
    mock_client = Mock()
    mock_client.conversation = Mock()
    mock_client.get_messages = Mock()

    server = DemoServer(mock_client, "test_bot")

    assert server.client == mock_client
    assert server.peer == "test_bot"


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
