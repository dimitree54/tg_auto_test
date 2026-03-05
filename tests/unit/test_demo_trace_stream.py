import asyncio
from typing import cast

from fastapi.testclient import TestClient
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters

from tests.unit.helpers_ptb_app import build_test_application
from tests.unit.sse_helpers import make_png_bytes, parse_sse_events, parse_sse_messages
from tg_auto_test.demo_ui.server.demo_server import DemoClientProtocol, DemoServer
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


def test_message_route_emits_trace_events() -> None:
    client = ServerlessTelegramClient(build_test_application)
    server = DemoServer(cast(DemoClientProtocol, client), "test_bot")
    app = server.create_app()

    with TestClient(app) as http:
        response = http.post("/api/message", json={"text": "hello"}, headers={"X-Demo-Trace-Id": "trace-123"})

    events = parse_sse_events(response)
    assert response.status_code == 200
    assert events[-1] == {"event": "done", "data": "[DONE]"}
    trace_events = [event["data"] for event in events if event["event"] == "trace"]
    assert any(event["trace_id"] == "trace-123" and event["name"] == "request_started" for event in trace_events)
    assert any(event["name"] == "bot_api_call" for event in trace_events)
    messages = [event["data"] for event in events if event["event"] == "message"]
    assert len(messages) == 1
    assert messages[0]["text"] == "hello"


def test_callback_route_uses_sse_trace_stream() -> None:
    client = ServerlessTelegramClient(build_test_application)
    server = DemoServer(cast(DemoClientProtocol, client), "test_bot")
    app = server.create_app()

    with TestClient(app) as http:
        initial = http.post("/api/message", json={"text": "/inline"})
        message = parse_sse_messages(initial)[0]
        response = http.post(
            "/api/callback",
            json={"message_id": message["message_id"], "data": "opt_a"},
            headers={"X-Demo-Trace-Id": "callback-1"},
        )

    events = parse_sse_events(response)
    trace_events = [event["data"] for event in events if event["event"] == "trace"]
    messages = [event["data"] for event in events if event["event"] == "message"]
    assert response.status_code == 200
    assert any(event["trace_id"] == "callback-1" and event["name"] == "request_started" for event in trace_events)
    assert any(message["text"] == "You chose: opt_a" for message in messages)


async def _raising_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message and update.message.text:
        await asyncio.sleep(0)
        raise RuntimeError("boom")


def _build_raising_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _raising_handler))
    return app


def test_handler_exception_is_streamed_and_error_handler_is_removed() -> None:
    client = ServerlessTelegramClient(_build_raising_app)
    server = DemoServer(cast(DemoClientProtocol, client), "test_bot")
    app = server.create_app()

    with TestClient(app) as http:
        assert client._application.error_handlers == {}  # noqa: SLF001
        response = http.post("/api/message", json={"text": "explode"})
        assert client._application.error_handlers == {}  # noqa: SLF001

    trace_events = [event["data"] for event in parse_sse_events(response) if event["event"] == "trace"]
    assert response.status_code == 200
    assert any(event["name"] == "exception" for event in trace_events)
    assert any(event["name"] == "request_failed" for event in trace_events)


def test_file_trace_payload_omits_raw_bytes() -> None:
    client = ServerlessTelegramClient(build_test_application)
    server = DemoServer(cast(DemoClientProtocol, client), "test_bot")
    app = server.create_app()

    with TestClient(app) as http:
        response = http.post(
            "/api/photo",
            files={"file": ("image.png", make_png_bytes(), "image/png")},
            headers={"X-Demo-Trace-Id": "photo-1"},
        )

    trace_events = [event["data"] for event in parse_sse_events(response) if event["event"] == "trace"]
    photo_calls = [
        event["payload"]["call"]
        for event in trace_events
        if event["name"] == "bot_api_call" and event["payload"]["call"]["api_method"] == "sendPhoto"
    ]
    assert len(photo_calls) == 1
    assert "file" in photo_calls[0]
    assert "data" not in photo_calls[0]["file"]
