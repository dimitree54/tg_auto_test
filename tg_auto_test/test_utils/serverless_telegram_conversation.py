from pathlib import Path
from types import TracebackType
from typing import Protocol

from tg_auto_test.test_utils.models import ServerlessMessage


class ConversationClient(Protocol):
    async def process_text_message(self, text: str) -> ServerlessMessage: ...

    async def process_file_message(
        self,
        file: Path | bytes,
        *,
        caption: str = "",
        force_document: bool = False,
        voice_note: bool = False,
        video_note: bool = False,
    ) -> ServerlessMessage: ...

    def pop_response(self) -> ServerlessMessage: ...

    async def process_callback_query(self, message_id: int, data: str) -> ServerlessMessage: ...


class ServerlessTelegramConversation:
    def __init__(self, client: ConversationClient) -> None:
        self._client = client

    async def __aenter__(self) -> "ServerlessTelegramConversation":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        del exc_type, exc, exc_tb

    async def send_message(self, text: str) -> None:
        await self._client.process_text_message(text)

    async def send_file(
        self,
        file: Path | bytes,
        *,
        caption: str = "",
        force_document: bool = False,
        voice_note: bool = False,
        video_note: bool = False,
    ) -> None:
        await self._client.process_file_message(
            file,
            caption=caption,
            force_document=force_document,
            voice_note=voice_note,
            video_note=video_note,
        )

    async def get_response(self) -> ServerlessMessage:
        return self._client.pop_response()

    async def click_inline_button(self, message_id: int, callback_data: str) -> ServerlessMessage:
        return await self._client.process_callback_query(message_id, callback_data)
