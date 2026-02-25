"""ServerlessMessage class for Telegram bot testing infrastructure."""

from dataclasses import dataclass, field

from telethon.tl.custom.file import File as TelethonFile
from telethon.tl.types import Document, MessageMediaInvoice, Photo

from tg_auto_test.test_utils.json_types import JsonValue
from tg_auto_test.test_utils.serverless_message_helpers import (
    ClickCallback,
    FileData,
    ReplyMarkup,
)
from tg_auto_test.test_utils.serverless_message_properties import ServerlessMessageProperties


@dataclass(slots=True)
class ServerlessMessage(ServerlessMessageProperties):
    """Response from the serverless client, mimicking Telethon's Message.

    Properties (.photo, .document, .voice, .video_note, .file) return real
    Telethon TL types so that test assertions are identical across backends.
    """

    id: int = 0
    text: str = ""
    _media_photo: Photo | None = None
    _media_document: Document | None = None
    _invoice_data: MessageMediaInvoice | None = None
    _poll_data: JsonValue | None = None
    _raw_bytes: bytes = b""
    _file_store: dict[str, FileData] = field(default_factory=dict, repr=False)
    _response_file_id: str = ""
    _reply_markup_data: ReplyMarkup | None = field(default=None, repr=False)
    _click_callback: ClickCallback | None = field(default=None, repr=False)
    _file_cache: TelethonFile | None = field(default=None, repr=False)

    async def download_media(
        self, file: object = None, *, thumb: object = None, progress_callback: object = None
    ) -> bytes | None:
        """Download media bytes, matching Telethon's Message.download_media signature.

        Returns raw bytes from the bot's response (for uploads like mirror)
        or from the in-memory file store (for echo/passthrough).
        """
        if thumb is not None:
            raise NotImplementedError("thumb parameter not supported")
        if progress_callback is not None:
            raise NotImplementedError("progress_callback parameter not supported")

        # file=None means same as file=bytes for backward compatibility
        if file is not None and file is not bytes:
            raise NotImplementedError("ServerlessTelegramClient only supports file=bytes or file=None")

        if self._raw_bytes:
            return self._raw_bytes
        if self._response_file_id and self._response_file_id in self._file_store:
            return self._file_store[self._response_file_id].data
        return None

    async def click(
        self,
        i: int | None = None,
        j: int | None = None,
        *,
        text: str | None = None,
        filter: object = None,  # noqa: A002
        data: bytes | None = None,
        share_phone: bool | None = None,
        share_geo: object = None,
        password: str | None = None,
        open_url: bool | None = None,
    ) -> "ServerlessMessage":
        """Simulate pressing an inline button, matching Telethon's message.click signature.

        Delegates to the parent client's callback-query handler.
        """
        # Check that at least one parameter is provided
        if all(param is None for param in [i, j, text, filter, data, share_phone, share_geo, password, open_url]):
            raise ValueError("At least one parameter must be provided")

        # Raise NotImplementedError for unsupported parameters
        if i is not None:
            raise NotImplementedError("i parameter not supported")
        if j is not None:
            raise NotImplementedError("j parameter not supported")
        if text is not None:
            raise NotImplementedError("text parameter not supported")
        if filter is not None:
            raise NotImplementedError("filter parameter not supported")
        if share_phone is not None:
            raise NotImplementedError("share_phone parameter not supported")
        if share_geo is not None:
            raise NotImplementedError("share_geo parameter not supported")
        if password is not None:
            raise NotImplementedError("password parameter not supported")
        if open_url is not None:
            raise NotImplementedError("open_url parameter not supported")

        # Only data parameter is supported
        if data is None:
            raise ValueError("data parameter is required when other parameters are not supported")

        if self._click_callback is None:
            raise RuntimeError("click() requires a client reference (_click_callback).")
        return await self._click_callback(self.id, data.decode())
