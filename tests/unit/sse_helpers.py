"""Helpers for parsing SSE (Server-Sent Events) responses in tests."""

import json

from httpx import Response


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
