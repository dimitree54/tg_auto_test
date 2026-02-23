"""Telethon-compatible message wrapper for ServerlessTelegramClient."""

from typing import Protocol

from tg_auto_test.test_utils.models import ServerlessMessage


class CallbackClient(Protocol):
    """Protocol for clients that can process callback queries."""

    async def process_callback_query(self, message_id: int, data: str) -> ServerlessMessage: ...


class TelethonCompatibleMessage:
    """Message wrapper that provides Telethon-compatible click() method."""

    def __init__(self, message_id: int, client: CallbackClient) -> None:
        self.id = message_id
        self._client = client

    async def click(self, data: bytes | str) -> ServerlessMessage:
        """Click a button on this message using Telethon-style API."""
        if isinstance(data, bytes):
            data = data.decode()
        return await self._client.process_callback_query(self.id, data)
