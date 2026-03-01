"""Tests for Demo UI serialization of HTML-formatted messages."""

import pytest

from tests.unit.html_test_app import build_html_app
from tg_auto_test.demo_ui.server.file_store import FileStore
from tg_auto_test.demo_ui.server.serialize import serialize_message
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


@pytest.mark.asyncio
async def test_demo_serialize_bold_from_html_bot() -> None:
    """Full round-trip: bot HTML -> ServerlessMessage -> serialize_message -> entities in API."""
    client = ServerlessTelegramClient(build_application=build_html_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/bold")
            msg = await conv.get_response()
        file_store = FileStore()
        response = await serialize_message(msg, file_store)
        assert response.text == "bold"
        assert len(response.entities) == 1
        assert response.entities[0]["type"] == "bold"
        assert response.entities[0]["offset"] == 0
        assert response.entities[0]["length"] == 4
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_demo_serialize_mixed_html_entities() -> None:
    """Full round-trip: mixed HTML -> correct entities for frontend rendering."""
    client = ServerlessTelegramClient(build_application=build_html_app)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/mixed")
            msg = await conv.get_response()
        file_store = FileStore()
        response = await serialize_message(msg, file_store)
        assert response.text == "Send text or photo to translate."
        assert len(response.entities) == 2
        assert response.entities[0]["type"] == "bold"
        assert response.entities[1]["type"] == "bold"
    finally:
        await client.disconnect()
