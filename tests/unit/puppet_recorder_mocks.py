"""Mock classes shared by puppet recorder tests."""

from unittest.mock import AsyncMock  # noqa: TID251

from tg_auto_test.test_utils.models import ServerlessMessage


class MockRecorderConversation:
    """Mock conversation context manager for recorder testing."""

    def __init__(self, response: ServerlessMessage) -> None:
        self._response: ServerlessMessage | None = response
        self.send_message = AsyncMock()
        self.send_file = AsyncMock()

    async def get_response(self) -> ServerlessMessage:
        if self._response is None:
            raise RuntimeError("No pending response.")
        resp = self._response
        self._response = None
        return resp

    async def __aenter__(self) -> "MockRecorderConversation":
        return self

    async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        pass


class MockRecorderClient:
    """Mock client for puppet recorder testing."""

    def __init__(self, response: ServerlessMessage | None = None) -> None:
        self._response = response or ServerlessMessage(id=1, text="echo")
        self.connect = AsyncMock()
        self.disconnect = AsyncMock()
        self.get_messages = AsyncMock()
        self._call_log: list[object] = []

    def conversation(self, peer: object, *, timeout: float = 60.0) -> MockRecorderConversation:
        del peer, timeout
        return MockRecorderConversation(self._response)

    async def get_input_entity(self, peer: object) -> object:
        del peer
        from telethon.tl.types import InputPeerUser  # noqa: PLC0415

        return InputPeerUser(user_id=999_999, access_hash=0)

    async def __call__(self, request: object) -> None:
        self._call_log.append(request)
