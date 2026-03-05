"""Helpers for parsing SSE (Server-Sent Events) responses in tests."""

import io
import json

from httpx import Response
from PIL import Image


def parse_sse_messages(response: Response) -> list[dict]:
    """Parse SSE events from a streaming response, returning message dicts.

    Skips the ``[DONE]`` sentinel.
    """
    messages: list[dict] = []
    for line in response.text.splitlines():
        if not line.startswith("data: "):
            continue
        payload = line[len("data: ") :]
        if payload == "[DONE]":
            continue
        messages.append(json.loads(payload))
    return messages


def make_png_bytes() -> bytes:
    """Return a minimal valid PNG image (2x2 red)."""
    buf = io.BytesIO()
    Image.new("RGB", (2, 2), color="red").save(buf, format="PNG")
    return buf.getvalue()
