"""Helpers for parsing SSE (Server-Sent Events) responses in tests."""

import io
import json

from httpx import Response
from PIL import Image


def parse_sse_events(response: Response) -> list[dict[str, object]]:
    """Parse SSE events from a streaming response."""
    events: list[dict[str, object]] = []
    for chunk in response.text.split("\n\n"):
        lines = [line for line in chunk.splitlines() if line]
        if not lines:
            continue
        event_name = "message"
        data_parts: list[str] = []
        for line in lines:
            if line.startswith("event: "):
                event_name = line[len("event: ") :]
            elif line.startswith("data: "):
                data_parts.append(line[len("data: ") :])
        if not data_parts:
            continue
        payload = "\n".join(data_parts)
        if payload == "[DONE]":
            events.append({"event": "done", "data": payload})
            continue
        events.append({"event": event_name, "data": json.loads(payload)})
    return events


def parse_sse_messages(response: Response) -> list[dict]:
    """Parse SSE message events from a streaming response."""
    return [event["data"] for event in parse_sse_events(response) if event["event"] == "message"]


def make_png_bytes() -> bytes:
    """Return a minimal valid PNG image (2x2 red)."""
    buf = io.BytesIO()
    Image.new("RGB", (2, 2), color="red").save(buf, format="PNG")
    return buf.getvalue()
