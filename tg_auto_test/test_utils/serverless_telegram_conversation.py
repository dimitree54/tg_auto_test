from pathlib import Path
from types import TracebackType
from typing import Protocol

from tg_auto_test.test_utils.models import ServerlessMessage


class ConversationClient(Protocol):
    async def _process_text_message(self, text: str) -> ServerlessMessage: ...

    async def _process_file_message(
        self,
        file: Path | bytes,
        *,
        caption: str = "",
        force_document: bool = False,
        voice_note: bool = False,
        video_note: bool = False,
    ) -> ServerlessMessage: ...

    def _pop_response(self) -> ServerlessMessage: ...

    async def _process_callback_query(self, message_id: int, data: str) -> ServerlessMessage: ...


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

    async def send_message(self, text: str) -> ServerlessMessage:
        return await self._client._process_text_message(text)  # noqa: SLF001

    async def send_file(
        self,
        file: Path | bytes,
        *,
        caption: str = "",
        force_document: bool = False,
        voice_note: bool = False,
        video_note: bool = False,
    ) -> ServerlessMessage:
        return await self._client._process_file_message(  # noqa: SLF001
            file,
            caption=caption,
            force_document=force_document,
            voice_note=voice_note,
            video_note=video_note,
        )

    async def get_response(self, message: object = None, *, timeout: float | None = None) -> ServerlessMessage:
        if message is not None:
            raise NotImplementedError("message parameter not supported in serverless mode")
        if timeout is not None:
            raise NotImplementedError("timeout parameter not supported in serverless mode")
        return self._client._pop_response()  # noqa: SLF001

    async def get_reply(self, message: object = None, *, timeout: float | None = None) -> ServerlessMessage:
        raise NotImplementedError("get_reply() not supported in serverless mode")

    async def get_edit(self, message: object = None, *, timeout: float | None = None) -> ServerlessMessage:
        raise NotImplementedError("get_edit() not supported in serverless mode")
