"""Mock classes for demo server testing."""

from unittest.mock import AsyncMock  # noqa: TID251

from tg_auto_test.test_utils.models import ServerlessMessage


class MockConversation:
    """Mock conversation for testing demo server."""

    def __init__(self, response: ServerlessMessage) -> None:
        self._response: ServerlessMessage | None = response

    async def get_response(self) -> ServerlessMessage:
        if self._response is None:
            raise RuntimeError("No pending response.")
        resp = self._response
        self._response = None
        return resp

    async def __aenter__(self) -> "MockConversation":
        """Enter the async context manager."""
        return self

    async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> object:
        """Exit the async context manager."""
        return None


class MockDemoClient:
    """Mock demo client for testing demo server routes."""

    def __init__(self) -> None:
        self.connect = AsyncMock()
        self.disconnect = AsyncMock()
        self.get_messages = AsyncMock()
        self._call_log: list = []
        self._response = ServerlessMessage(id=456, text="You voted for: Red")

    def conversation(self, peer: object, *, timeout: float = 60.0) -> MockConversation:  # noqa: ARG002
        """Create a conversation context manager."""
        return MockConversation(self._response)

    def _pop_response(self) -> ServerlessMessage:
        """Private method for testing - matches implementation."""
        return self._response

    async def get_input_entity(self, peer: object) -> object:  # noqa: ARG002
        """Mock get_input_entity implementation."""
        from telethon.tl.types import InputPeerUser  # noqa: PLC0415

        return InputPeerUser(user_id=999_999, access_hash=0)

    async def __call__(self, request: object) -> None:
        """Mock TL request execution."""
        self._call_log.append(request)
        return None
