"""Unit tests for the file store implementation."""

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
