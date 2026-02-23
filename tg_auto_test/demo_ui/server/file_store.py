"""In-memory file storage for the demo server."""


class FileStore:
    """In-memory storage for uploaded and response files."""

    def __init__(self) -> None:
        # file_id -> (filename, content_type, bytes)
        self._files: dict[str, tuple[str, str, bytes]] = {}

    def store(self, file_id: str, filename: str, content_type: str, data: bytes) -> None:
        """Store file data under the given file_id."""
        self._files[file_id] = (filename, content_type, data)

    def get(self, file_id: str) -> tuple[str, str, bytes] | None:
        """Get file data by file_id. Returns (filename, content_type, bytes) or None."""
        return self._files.get(file_id)

    def exists(self, file_id: str) -> bool:
        """Check if file_id exists in storage."""
        return file_id in self._files

    def clear(self) -> None:
        """Clear all stored files."""
        self._files.clear()

    def __contains__(self, file_id: str) -> bool:
        """Check if file_id exists using 'in' operator."""
        return file_id in self._files
