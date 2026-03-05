"""Demo route helpers for trace-streamed actions."""

from uuid import uuid4

from fastapi import Request
from fastapi.responses import StreamingResponse

from tg_auto_test.demo_ui.server.serverless_trace_runner import stream_serverless_action
from tg_auto_test.demo_ui.server.serverless_trace_support import (
    build_callback_payload,
    build_file_payload,
    build_poll_payload,
    build_text_payload,
    run_payment_flow,
)
from tg_auto_test.demo_ui.server.telethon_fallback_streams import (
    stream_callback_fallback,
    stream_file_fallback,
    stream_payment_fallback,
    stream_poll_fallback,
    stream_text_fallback,
)


def _trace_id_from_request(request: Request) -> str:
    return request.headers.get("X-Demo-Trace-Id") or f"demo-{uuid4()}"


def _supports_serverless_tracing(client: object) -> bool:
    return all(
        hasattr(client, attr)
        for attr in ("_application", "_handle_click", "_helpers", "_invoices", "_outbox", "_poll_tracker", "_request")
    )


async def _process_payload(demo_server: object, payload: dict[str, object]) -> None:
    demo_server.client._outbox.clear()  # noqa: SLF001
    await demo_server.client._update_processor.process_update(demo_server.client, payload)  # noqa: SLF001


def stream_text_action(demo_server: object, request: Request, text: str) -> StreamingResponse:
    trace_id = _trace_id_from_request(request)
    if not _supports_serverless_tracing(demo_server.client):
        return stream_text_fallback(demo_server, text, trace_id)
    payload, summary = build_text_payload(demo_server.client, text)

    async def _run() -> None:
        await _process_payload(demo_server, payload)

    return stream_serverless_action(
        demo_server,
        action_name="send_text",
        request_payload=summary,
        trace_id=trace_id,
        run_action=_run,
    )


def stream_file_action(
    demo_server: object,
    request: Request,
    data: bytes,
    *,
    caption: str = "",
    force_document: bool = False,
    voice_note: bool = False,
    video_note: bool = False,
) -> StreamingResponse:
    trace_id = _trace_id_from_request(request)
    if not _supports_serverless_tracing(demo_server.client):
        return stream_file_fallback(
            demo_server,
            data,
            trace_id,
            caption=caption,
            force_document=force_document,
            voice_note=voice_note,
            video_note=video_note,
        )
    payload, summary = build_file_payload(
        demo_server.client,
        data,
        caption=caption,
        force_document=force_document,
        voice_note=voice_note,
        video_note=video_note,
    )

    async def _run() -> None:
        await _process_payload(demo_server, payload)

    return stream_serverless_action(
        demo_server,
        action_name="send_file",
        request_payload=summary,
        trace_id=trace_id,
        run_action=_run,
    )


def stream_payment_action(demo_server: object, request: Request, message_id: int) -> StreamingResponse:
    trace_id = _trace_id_from_request(request)
    if not _supports_serverless_tracing(demo_server.client):
        return stream_payment_fallback(demo_server, message_id, trace_id)

    async def _run() -> None:
        demo_server.client._outbox.clear()  # noqa: SLF001
        await run_payment_flow(demo_server.client, message_id)

    return stream_serverless_action(
        demo_server,
        action_name="pay_stars",
        request_payload={"message_id": message_id},
        trace_id=trace_id,
        run_action=_run,
        on_action_name="pay_stars",
    )


def stream_callback_action(
    demo_server: object,
    request: Request,
    message_id: int,
    data: str,
) -> StreamingResponse:
    trace_id = _trace_id_from_request(request)
    if not _supports_serverless_tracing(demo_server.client):
        return stream_callback_fallback(demo_server, message_id, data, trace_id)
    payload, summary = build_callback_payload(demo_server.client, message_id, data)

    async def _run() -> None:
        await _process_payload(demo_server, payload)

    return stream_serverless_action(
        demo_server,
        action_name="callback",
        request_payload=summary,
        trace_id=trace_id,
        run_action=_run,
        on_action_name="click_button",
    )


def stream_poll_action(
    demo_server: object,
    request: Request,
    message_id: int,
    option_ids: list[int],
) -> StreamingResponse:
    trace_id = _trace_id_from_request(request)
    if not _supports_serverless_tracing(demo_server.client):
        return stream_poll_fallback(demo_server, message_id, option_ids, trace_id)
    payload, summary = build_poll_payload(demo_server.client, message_id, option_ids)

    async def _run() -> None:
        await _process_payload(demo_server, payload)

    return stream_serverless_action(
        demo_server,
        action_name="poll_vote",
        request_payload=summary,
        trace_id=trace_id,
        run_action=_run,
        on_action_name="poll_vote",
    )
