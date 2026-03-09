from pathlib import Path
from types import TracebackType

from tg_auto_test.test_utils.models import ServerlessMessage
from tg_auto_test.test_utils.serverless_conversation_runtime import ConversationClient, ConversationRuntime


class ServerlessTelegramConversation:
    def __init__(self, client: ConversationClient, *, timeout: float = 60.0) -> None:
        self._client = client
        self._runtime = ConversationRuntime(client, timeout=timeout)

    async def __aenter__(self) -> "ServerlessTelegramConversation":
        self._runtime.install()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        del exc_type, exc, exc_tb
        self._runtime.restore()

    async def send_message(self, text: str) -> ServerlessMessage:
        before_tasks = self._runtime.begin_action()
        payload, msg = self._client._helpers.base_message_update(self._client._chat_id)
        msg["text"] = text
        if text.startswith("/"):
            msg["entities"] = [
                {"offset": 0, "length": text.find(" ") if " " in text else len(text), "type": "bot_command"}
            ]
        await self._client._update_processor.process_update(self._client, payload)
        self._runtime.finish_action(before_tasks)
        return ServerlessMessage(id=int(msg["message_id"]), text=text)

    async def send_file(
        self,
        file: Path | bytes,
        *,
        caption: str = "",
        force_document: bool = False,
        voice_note: bool = False,
        video_note: bool = False,
    ) -> ServerlessMessage:
        before_tasks = self._runtime.begin_action()
        result = await self._client._process_file_message(
            file,
            caption=caption,
            force_document=force_document,
            voice_note=voice_note,
            video_note=video_note,
        )
        self._runtime.finish_action(before_tasks)
        return result

    async def get_response(self, message: object = None, *, timeout: float | None = None) -> ServerlessMessage:
        if message is not None:
            raise NotImplementedError("message parameter not supported in serverless mode")
        return await self._runtime.get_response(timeout)

    async def get_reply(self, message: object = None, *, timeout: float | None = None) -> ServerlessMessage:
        raise NotImplementedError("get_reply() not supported in serverless mode")

    async def get_edit(self, message: object = None, *, timeout: float | None = None) -> ServerlessMessage:
        if message is not None:
            raise NotImplementedError("message parameter not supported in serverless mode")
        return await self._runtime.get_edit(timeout)

    def cancel(self) -> None:
        raise NotImplementedError("cancel() is not supported in serverless testing mode")

    async def cancel_all(self) -> None:
        raise NotImplementedError("cancel_all() is not supported in serverless testing mode")

    async def wait_event(self, event: object, *, timeout: float | None = None) -> object:
        del event, timeout
        raise NotImplementedError("wait_event() requires the event system and is not supported")

    def wait_read(self, message: object = None, *, timeout: float | None = None) -> object:
        del message, timeout
        raise NotImplementedError("wait_read() requires read receipt tracking and is not supported")

    def mark_read(self, message: object = None) -> None:
        del message
        raise NotImplementedError("mark_read() requires read receipt tracking and is not supported")

    @property
    def chat(self) -> object:
        raise NotImplementedError("chat requires entity resolution")

    @property
    def chat_id(self) -> int | None:
        raise NotImplementedError("chat_id is not tracked in serverless mode")

    @property
    def input_chat(self) -> object:
        raise NotImplementedError("input_chat requires entity resolution")

    @property
    def is_channel(self) -> bool:
        raise NotImplementedError("is_channel requires entity resolution")

    @property
    def is_group(self) -> bool:
        raise NotImplementedError("is_group requires entity resolution")

    @property
    def is_private(self) -> bool:
        raise NotImplementedError("is_private requires entity resolution")

    async def get_chat(self) -> object:
        raise NotImplementedError("get_chat requires entity resolution")

    async def get_input_chat(self) -> object:
        raise NotImplementedError("get_input_chat requires entity resolution")
