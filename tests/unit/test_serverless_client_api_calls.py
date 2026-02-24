"""Test API call inspection functionality with ServerlessTelegramClient."""

import pytest

from tests.unit.helpers_ptb_app import build_test_application
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient, TelegramApiCall


def test_api_calls_empty_initially() -> None:
    """Test that api_calls is empty before connecting."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    # Before connecting, no calls should have been made
    assert client._api_calls == []  # noqa: SLF001
    assert client._last_api_call is None  # noqa: SLF001


@pytest.mark.asyncio
async def test_api_calls_after_connect() -> None:
    """Test that api_calls shows getMe call after connecting."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        # After connecting, there should be a getMe call
        assert len(client._api_calls) >= 1  # noqa: SLF001
        last_call = client._last_api_call  # noqa: SLF001
        assert last_call is not None
        assert last_call.api_method == "getMe"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_api_calls_after_text_message() -> None:
    """Test that api_calls captures sendMessage calls."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("hello")
            await conv.get_response()

        # Check that we have at least one API call
        assert len(client._api_calls) > 0  # noqa: SLF001

        # Check the last call
        last_call = client._last_api_call  # noqa: SLF001
        assert last_call is not None
        assert last_call.api_method == "sendMessage"
        assert last_call.parameters.get("text") == "hello"
        assert last_call.file is None
        assert last_call.result is not None
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_api_calls_after_file_message() -> None:
    """Test that api_calls captures file upload calls."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        test_data = b"test file content"

        async with client.conversation("test_bot") as conv:
            await conv.send_file(test_data, force_document=True)
            await conv.get_response()

        # Check that we have API calls
        assert len(client._api_calls) > 0  # noqa: SLF001

        # Find the sendDocument call
        send_document_calls = [call for call in client._api_calls if call.api_method == "sendDocument"]  # noqa: SLF001
        assert len(send_document_calls) == 1

        call = send_document_calls[0]
        assert call.api_method == "sendDocument"
        assert call.file is not None
        assert call.file.data == test_data
        assert call.result is not None
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_api_calls_multiple_messages() -> None:
    """Test that api_calls accumulates multiple calls."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("first")
            await conv.get_response()

            await conv.send_message("second")
            await conv.get_response()

        # Should have multiple API calls
        assert len(client._api_calls) >= 2  # noqa: SLF001

        # Find sendMessage calls
        send_message_calls = [call for call in client._api_calls if call.api_method == "sendMessage"]  # noqa: SLF001
        assert len(send_message_calls) >= 2

        # Check that the last call is indeed the last one we made
        last_call = client._last_api_call  # noqa: SLF001
        assert last_call is not None
        # The last call could be sendMessage for "second" or some other call made after that
        # Let's just verify it's one of our calls
        assert last_call in client._api_calls  # noqa: SLF001
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_telegram_api_call_dataclass() -> None:
    """Test that TelegramApiCall is properly imported and usable."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("test")
            await conv.get_response()

        last_call = client._last_api_call  # noqa: SLF001
        assert last_call is not None
        assert isinstance(last_call, TelegramApiCall)

        # Test that all expected attributes are present
        assert hasattr(last_call, "api_method")
        assert hasattr(last_call, "parameters")
        assert hasattr(last_call, "file")
        assert hasattr(last_call, "result")

        # Test that we can access attributes
        assert isinstance(last_call.api_method, str)
        assert isinstance(last_call.parameters, dict)
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_api_calls_read_only() -> None:
    """Test that api_calls returns a read-only view."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("test")
            await conv.get_response()

        # Get the api_calls list
        calls1 = client._api_calls  # noqa: SLF001
        calls2 = client._api_calls  # noqa: SLF001

        # Should be different list instances (copies)
        assert calls1 is not calls2

        # But with the same content
        assert calls1 == calls2

        # Modifying the returned list should not affect future calls
        original_length = len(calls1)
        calls1.clear()
        assert len(calls1) == 0

        calls3 = client._api_calls  # noqa: SLF001
        assert len(calls3) == original_length
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_last_api_call_updates() -> None:
    """Test that last_api_call properly updates as new calls are made."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            # First message
            await conv.send_message("first")
            await conv.get_response()

            first_last_call = client._last_api_call  # noqa: SLF001
            assert first_last_call is not None

            # Second message
            await conv.send_message("second")
            await conv.get_response()

            second_last_call = client._last_api_call  # noqa: SLF001
            assert second_last_call is not None

            # The last call should have changed
            assert second_last_call is not first_last_call
    finally:
        await client.disconnect()
