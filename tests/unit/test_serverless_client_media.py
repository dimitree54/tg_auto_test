"""Test media handling with ServerlessTelegramClient."""

from io import BytesIO

from PIL import Image
import pytest

from tests.unit.helpers_ptb_app import build_test_application
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


def _create_test_png() -> bytes:
    """Create a minimal 2x2 PNG image for testing."""
    img = Image.new("RGB", (2, 2), color="red")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def _create_test_document() -> bytes:
    """Create a test document (text file) for testing."""
    return b"This is a test document content."


@pytest.mark.asyncio
async def test_photo_echo() -> None:
    """Test sending a photo and receiving it back."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            test_png = _create_test_png()

            await conv.send_file(test_png)
            msg = await conv.get_response()

            # Check that photo is set
            assert msg.photo is not None
            assert msg.document is None

            # Check that we can download the media
            downloaded = await msg.download_media(file=bytes)
            assert downloaded is not None
            assert isinstance(downloaded, bytes)
            assert len(downloaded) > 0
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_document_echo() -> None:
    """Test sending a document and receiving it back."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            test_doc = _create_test_document()

            await conv.send_file(test_doc, force_document=True)
            msg = await conv.get_response()

            # Check that document is set
            assert msg.document is not None
            assert msg.photo is None

            # Check file properties
            assert msg.file is not None
            assert msg.file.name is not None
            assert msg.file.mime_type is not None

            # Check that we can download the media
            downloaded = await msg.download_media(file=bytes)
            assert downloaded is not None
            assert isinstance(downloaded, bytes)
            assert len(downloaded) > 0
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_photo_file_properties() -> None:
    """Test that photo file properties are accessible."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            test_png = _create_test_png()

            await conv.send_file(test_png)
            msg = await conv.get_response()

            assert msg.photo is not None
            assert msg.file is not None
            # File properties should be available
            assert hasattr(msg.file, "size")
            assert hasattr(msg.file, "mime_type")
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_document_vs_photo_distinction() -> None:
    """Test that the library correctly distinguishes documents from photos."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            # Send PNG as photo (default behavior)
            test_png = _create_test_png()
            await conv.send_file(test_png)
            photo_msg = await conv.get_response()

            # Send PNG as document (forced)
            await conv.send_file(test_png, force_document=True)
            doc_msg = await conv.get_response()

            # Photo message should have photo but not document
            assert photo_msg.photo is not None
            assert photo_msg.document is None

            # Document message should have document but not photo
            assert doc_msg.document is not None
            assert doc_msg.photo is None
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_no_media_message() -> None:
    """Test that text messages have no media properties."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("hello")
            msg = await conv.get_response()

            assert msg.photo is None
            assert msg.document is None
            assert msg.voice is None
            assert msg.video_note is None
            assert msg.file is None

            # download_media should return None for non-media messages
            downloaded = await msg.download_media(file=bytes)
            assert downloaded is None
    finally:
        await client.disconnect()
