"""Trace event helpers for demo UI SSE streams."""

from datetime import UTC, datetime

from tg_auto_test.demo_ui.server.api_models import DemoTraceEvent, MessageResponse

_MESSAGE_EVENT = "message"
_TRACE_EVENT = "trace"
_DONE_SENTINEL = "data: [DONE]\n\n"


def build_trace_event(
    trace_id: str,
    scope: str,
    name: str,
    payload: dict[str, object] | None = None,
) -> DemoTraceEvent:
    """Create a demo trace event with a UTC timestamp."""
    return DemoTraceEvent(
        trace_id=trace_id,
        scope=scope,
        name=name,
        ts=datetime.now(UTC).isoformat(),
        payload=payload or {},
    )


def serialize_trace_event(event: DemoTraceEvent) -> str:
    """Serialize a trace event as SSE."""
    return f"event: {_TRACE_EVENT}\ndata: {event.model_dump_json()}\n\n"


def serialize_message_event(message: MessageResponse) -> str:
    """Serialize a bot message as SSE."""
    return f"event: {_MESSAGE_EVENT}\ndata: {message.model_dump_json()}\n\n"


def serialize_done_event() -> str:
    """Serialize the final SSE sentinel."""
    return _DONE_SENTINEL
