"""Hook and state helpers for serverless demo trace streaming."""

import asyncio
from collections.abc import Callable
import traceback

from tg_auto_test.demo_ui.server.trace_stream import build_trace_event
from tg_auto_test.test_utils.models import ServerlessMessage, TelegramApiCall
from tg_auto_test.test_utils.response_processor import process_api_call


class TraceState:
    def __init__(self, trace_id: str, queue: "asyncio.Queue[object]") -> None:
        self.trace_id = trace_id
        self.queue = queue
        self.message_count = 0
        self.logged_errors: set[int] = set()

    def emit_trace(self, scope: str, name: str, payload: dict[str, object] | None = None) -> None:
        self.queue.put_nowait(build_trace_event(self.trace_id, scope, name, payload))

    def emit_message(self, message: ServerlessMessage) -> None:
        self.message_count += 1
        self.queue.put_nowait(message)

    def emit_exception(self, error: BaseException, phase: str) -> None:
        if id(error) in self.logged_errors:
            return
        self.logged_errors.add(id(error))
        self.emit_trace(
            "bot",
            "exception",
            {
                "exception_type": type(error).__name__,
                "message": str(error),
                "phase": phase,
                "traceback": "".join(traceback.format_exception(type(error), error, error.__traceback__)),
            },
        )

    def fail(self, detail: str) -> None:
        self.emit_trace("server", "request_failed", {"detail": detail})


def install_request_hook(client: object, state: TraceState) -> Callable[[TelegramApiCall], None]:
    request = client._request  # noqa: SLF001
    previous_hook = request.on_api_call
    outbox = client._outbox  # noqa: SLF001

    def _on_api_call(call: TelegramApiCall) -> None:
        state.emit_trace("bot", "bot_api_call", {"call": _safe_call_summary(call)})
        if call.api_method == "deleteMessage":
            _remove_message(outbox, int(call.parameters["message_id"]))
            return
        if call.api_method not in _MESSAGE_METHODS:
            return
        message = process_api_call(
            call, request.file_store, client._invoices, client._handle_click, client._poll_tracker
        )  # noqa: SLF001
        if message._is_edit:  # noqa: SLF001
            _replace_message(outbox, message)
        else:
            outbox.append(message)
        state.emit_message(message)
        state.emit_trace("bot", "message_emitted", {"message_id": message.id, "message_type": _message_kind(message)})

    request.on_api_call = _on_api_call
    return previous_hook


_MESSAGE_METHODS = {
    "sendMessage",
    "sendDocument",
    "sendVoice",
    "sendPhoto",
    "sendVideoNote",
    "sendVideo",
    "sendAnimation",
    "sendAudio",
    "sendSticker",
    "sendInvoice",
    "sendPoll",
    "editMessageText",
}


def _replace_message(outbox: object, message: ServerlessMessage) -> None:
    for index, existing in enumerate(outbox):
        if existing.id == message.id:
            outbox[index] = message
            return


def _remove_message(outbox: object, message_id: int) -> None:
    for index, existing in enumerate(outbox):
        if existing.id == message_id:
            del outbox[index]
            return


def _safe_call_summary(call: TelegramApiCall) -> dict[str, object]:
    summary: dict[str, object] = {"api_method": call.api_method, "parameters": dict(call.parameters)}
    if call.file is not None:
        summary["file"] = {
            "content_type": call.file.content_type,
            "filename": call.file.filename,
            "size_bytes": len(call.file.data),
        }
    return summary


def _message_kind(message: ServerlessMessage) -> str:
    if message.poll is not None:
        return "poll"
    if message.invoice is not None:
        return "invoice"
    if message.photo is not None:
        return "photo"
    if message.voice is not None:
        return "voice"
    if message.video_note is not None:
        return "video_note"
    if message.document is not None:
        return "document"
    return "text"
