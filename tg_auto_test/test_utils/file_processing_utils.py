"""File processing utilities without circular imports."""

from pathlib import Path

from tg_auto_test.test_utils.exceptions import BotNoResponseError
from tg_auto_test.test_utils.file_message_builder import build_file_payload
from tg_auto_test.test_utils.json_types import JsonValue
from tg_auto_test.test_utils.media_types import detect_content_type
from tg_auto_test.test_utils.models import FileData
from tg_auto_test.test_utils.poll_vote_handler import handle_send_vote_request_for_client
from tg_auto_test.test_utils.serverless_bot_callback_answer import ServerlessBotCallbackAnswer


def process_file_message_data(
    file: Path | bytes,
    *,
    caption: str = "",  # noqa: ARG001
    force_document: bool = False,
    voice_note: bool = False,
    video_note: bool = False,
) -> tuple[bytes, str, str, FileData]:
    """Process file data and return components needed for message building."""
    file_bytes = file if isinstance(file, bytes) else file.read_bytes()
    fname = file.name if isinstance(file, Path) else "file"
    content_type = detect_content_type(fname, force_document, voice_note, video_note)
    file_data = FileData(data=file_bytes, filename=fname, content_type=content_type)
    return file_bytes, fname, content_type, file_data


def build_file_message_payload(
    payload: dict[str, JsonValue],  # noqa: ARG001
    msg: dict[str, JsonValue],
    file_id: str,
    file: Path | bytes,
    file_bytes: bytes,
    caption: str,
    force_document: bool,
    voice_note: bool,
    video_note: bool,
) -> None:
    """Build file message payload."""
    build_file_payload(
        msg,
        file_id,
        file,
        file_bytes=file_bytes,
        caption=caption,
        force_document=force_document,
        voice_note=voice_note,
        video_note=video_note,
    )


async def process_complete_file_message(
    client: object,
    file: Path | bytes,
    *,
    caption: str = "",
    force_document: bool = False,
    voice_note: bool = False,
    video_note: bool = False,
) -> object:
    """Complete file message processing for the client."""
    client._outbox.clear()  # noqa: SLF001
    file_id = client._helpers.make_file_id()  # noqa: SLF001
    file_bytes, fname, _ct, file_data = process_file_message_data(
        file, caption=caption, force_document=force_document, voice_note=voice_note, video_note=video_note
    )
    client._request.file_store[file_id] = file_data  # noqa: SLF001
    payload, msg = client._helpers.base_message_update(client._chat_id)  # noqa: SLF001
    build_file_message_payload(payload, msg, file_id, file, file_bytes, caption, force_document, voice_note, video_note)
    return await client._process_message_update(payload)  # noqa: SLF001


async def handle_send_vote_request_for_client_wrapper(
    client: object,
    peer: object,
    message_id: int,
    option_bytes: list[bytes],  # noqa: ARG001
) -> object:
    """Handle send vote request for the client."""
    del peer
    return await handle_send_vote_request_for_client(
        client._poll_tracker,
        client._helpers,
        client._process_message_update,  # noqa: SLF001
        client._outbox,
        message_id,
        option_bytes,  # noqa: SLF001
    )


async def simulate_stars_payment_wrapper(client: object, invoice_message_id: int) -> None:
    """Simulate stars payment for the client."""
    client._stars_balance = await client._stars_payment_handler.simulate_payment(  # noqa: SLF001
        client,
        invoice_message_id,
        client._invoices,
        client._stars_balance,
        client._helpers,  # noqa: SLF001
    )


async def handle_click_wrapper(client: object, message_id: int, data: str) -> ServerlessBotCallbackAnswer:
    """Handle click for the client, matching Telethon's BotCallbackAnswer behaviour.

    Bot response messages are left in the outbox so that conv.get_response() can
    retrieve them, mirroring what happens with a real TelegramClient against the
    Telegram API.
    """
    calls_before = len(client._request.calls)  # noqa: SLF001
    try:
        await client._process_callback_query(message_id, data)  # noqa: SLF001
    except BotNoResponseError:
        pass  # Bot answered query without sending a message; outbox unchanged
    new_calls = client._request.calls[calls_before:]  # noqa: SLF001
    answer_text = ""
    for call in new_calls:
        if call.api_method == "answerCallbackQuery":
            answer_text = str(call.parameters.get("text", ""))
            break
    return ServerlessBotCallbackAnswer(message=answer_text)


def pop_client_response(client: object) -> object:
    """Pop response from client outbox."""
    if not client._outbox:
        raise RuntimeError("No pending response. Call send_message() first.")  # noqa: SLF001
    return client._outbox.popleft()  # noqa: SLF001


async def connect_client(client: object) -> None:
    """Connect client if not already connected."""
    if not client._connected:  # noqa: SLF001
        await client._application.initialize()  # noqa: SLF001
        client._connected = True  # noqa: SLF001


async def disconnect_client(client: object) -> None:
    """Disconnect client if connected."""
    if client._connected:  # noqa: SLF001
        await client._application.shutdown()  # noqa: SLF001
        client._connected = False  # noqa: SLF001
