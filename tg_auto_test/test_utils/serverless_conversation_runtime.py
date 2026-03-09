import asyncio
from collections import deque
from pathlib import Path
from typing import Protocol

from tg_auto_test.test_utils.models import ServerlessMessage, TelegramApiCall
from tg_auto_test.test_utils.poll_vote_handler import PollTracker
from tg_auto_test.test_utils.response_processor import _MESSAGE_METHODS, process_api_call
from tg_auto_test.test_utils.serverless_bot_callback_answer import ServerlessBotCallbackAnswer
from tg_auto_test.test_utils.serverless_client_helpers import ServerlessClientHelpers
from tg_auto_test.test_utils.serverless_outbox_utils import pop_message_by_id, remove_message
from tg_auto_test.test_utils.serverless_update_processor import ServerlessUpdateProcessor, _replace_edited_message
from tg_auto_test.test_utils.stub_request import StubTelegramRequest


class ConversationClient(Protocol):
    _chat_id: int
    _edit_outbox: deque[ServerlessMessage]
    _helpers: ServerlessClientHelpers
    _invoices: dict[int, dict[str, object]]
    _outbox: deque[ServerlessMessage]
    _poll_tracker: PollTracker | None
    _request: StubTelegramRequest
    _update_processor: ServerlessUpdateProcessor

    async def _process_file_message(
        self,
        file: Path | bytes,
        *,
        caption: str = "",
        force_document: bool = False,
        voice_note: bool = False,
        video_note: bool = False,
    ) -> ServerlessMessage: ...

    async def _handle_click(self, message_id: int, data: str) -> ServerlessBotCallbackAnswer: ...


class ConversationRuntime:
    def __init__(self, client: ConversationClient, *, timeout: float = 60.0) -> None:
        self._client = client
        self.timeout = timeout
        self.response_queue: asyncio.Queue[int] = asyncio.Queue()
        self.edit_queue: asyncio.Queue[ServerlessMessage] = asyncio.Queue()
        self.pending_tasks: set[asyncio.Task[object]] = set()
        self._previous_hook = client._request.on_api_call

    def install(self) -> None:
        self._client._request.on_api_call = self.on_api_call
        setattr(self._client, "_active_conversation_runtime", self)
        setattr(self._client, "_live_message_capture", True)

    def restore(self) -> None:
        self._client._request.on_api_call = self._previous_hook
        setattr(self._client, "_active_conversation_runtime", None)
        setattr(self._client, "_live_message_capture", False)
        self.pending_tasks.clear()

    def begin_action(self) -> set[asyncio.Task[object]]:
        self._client._outbox.clear()
        self._client._edit_outbox.clear()
        self._clear_queue(self.response_queue)
        self._clear_queue(self.edit_queue)
        self.pending_tasks.clear()
        return self._snapshot_tasks()

    def finish_action(self, before_tasks: set[asyncio.Task[object]]) -> None:
        self.pending_tasks = self._snapshot_tasks() - before_tasks

    def on_api_call(self, call: TelegramApiCall) -> None:
        if call.api_method == "deleteMessage":
            remove_message(self._client._outbox, int(call.parameters["message_id"]))
            return
        if call.api_method not in _MESSAGE_METHODS:
            return
        message = process_api_call(
            call,
            self._client._request.file_store,
            self._client._invoices,
            self._client._handle_click,
            self._client._poll_tracker,
        )
        if message._is_edit:  # noqa: SLF001
            _replace_edited_message(self._client._outbox, message)
            self._client._edit_outbox.append(message)
            self.edit_queue.put_nowait(message)
            return
        self._client._outbox.append(message)
        self.response_queue.put_nowait(message.id)

    async def get_response(self, timeout: float | None) -> ServerlessMessage:
        effective_timeout = self.timeout if timeout is None else timeout
        deadline = None if effective_timeout is None else asyncio.get_running_loop().time() + effective_timeout
        while True:
            message = self._pop_response_nowait()
            if message is not None:
                return message
            if not self.pending_tasks:
                raise RuntimeError("No pending response. Call send_message() first.")
            queue_task = asyncio.create_task(self.response_queue.get())
            remaining = None if deadline is None else max(0.0, deadline - asyncio.get_running_loop().time())
            done, _pending = await asyncio.wait(
                {queue_task, *self.pending_tasks},
                timeout=remaining,
                return_when=asyncio.FIRST_COMPLETED,
            )
            queue_result = self._finished_queue_result(queue_task)
            if queue_result is not None:
                message = pop_message_by_id(self._client._outbox, queue_result)
                if message is not None:
                    return message
                continue
            queue_task.cancel()
            try:
                await queue_task
            except asyncio.CancelledError:
                pass
            if not done:
                raise asyncio.TimeoutError
            self._handle_done_tasks(done)

    async def get_edit(self, timeout: float | None) -> ServerlessMessage:
        return await self._wait_for_queue(
            self.edit_queue,
            timeout,
            "No pending edit. The bot did not edit any message.",
        )

    async def _wait_for_queue(
        self,
        queue: "asyncio.Queue[ServerlessMessage]",
        timeout: float | None,
        empty_message: str,
    ) -> ServerlessMessage:
        effective_timeout = self.timeout if timeout is None else timeout
        deadline = None if effective_timeout is None else asyncio.get_running_loop().time() + effective_timeout
        while True:
            message = self._pop_nowait(queue)
            if message is not None:
                return message
            if not self.pending_tasks:
                raise RuntimeError(empty_message)
            queue_task = asyncio.create_task(queue.get())
            remaining = None if deadline is None else max(0.0, deadline - asyncio.get_running_loop().time())
            done, _pending = await asyncio.wait(
                {queue_task, *self.pending_tasks},
                timeout=remaining,
                return_when=asyncio.FIRST_COMPLETED,
            )
            queue_result = self._finished_queue_result(queue_task)
            if queue_result is not None:
                return queue_result
            queue_task.cancel()
            try:
                await queue_task
            except asyncio.CancelledError:
                pass
            if not done:
                raise asyncio.TimeoutError
            self._handle_done_tasks(done)

    def _handle_done_tasks(self, done: set[asyncio.Task[object]]) -> None:
        for task in done:
            self.pending_tasks.discard(task)
            if task.cancelled():
                continue
            error = task.exception()
            if error is not None:
                raise error

    @staticmethod
    def _snapshot_tasks() -> set[asyncio.Task[object]]:
        current_task = asyncio.current_task()
        return {task for task in asyncio.all_tasks() if task is not current_task and not task.done()}

    @staticmethod
    def _clear_queue(queue: "asyncio.Queue[ServerlessMessage] | asyncio.Queue[int]") -> None:
        while not queue.empty():
            queue.get_nowait()

    @staticmethod
    def _pop_nowait(queue: "asyncio.Queue[ServerlessMessage]") -> ServerlessMessage | None:
        if queue.empty():
            return None
        return queue.get_nowait()

    def _pop_response_nowait(self) -> ServerlessMessage | None:
        while not self.response_queue.empty():
            message_id = self.response_queue.get_nowait()
            message = pop_message_by_id(self._client._outbox, message_id)
            if message is not None:
                return message
        return None

    @staticmethod
    def _finished_queue_result(queue_task: asyncio.Task[object]) -> object | None:
        if queue_task.cancelled() or not queue_task.done():
            return None
        return queue_task.result()
