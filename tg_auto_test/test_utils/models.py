"""Data models for the serverless Telegram testing infrastructure.

ServerlessMessage mimics Telethon's Message interface so that the same
assertions work on both serverless and serverfull (real Telegram) backends.
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from telethon.tl.custom.file import File as TelethonFile
from telethon.tl.types import (
    Document,
    DocumentAttributeAudio,
    DocumentAttributeVideo,
    MessageMediaInvoice,
    Photo,
)

from tg_auto_test.test_utils.json_types import JsonValue

ReplyMarkup = dict[str, JsonValue]
ClickCallback = Callable[[int, str], Awaitable["ServerlessMessage"]]


@dataclass(frozen=True, slots=True)
class ServerlessButton:
    """Wraps a raw button dict to expose a ``.text`` attribute like Telethon."""

    text: str
    callback_data: str = ""


def _wrap_button_row(row: JsonValue) -> list[ServerlessButton]:
    """Convert a raw JSON row of buttons into ServerlessButton objects."""
    if not isinstance(row, list):
        return []
    return [
        ServerlessButton(text=str(btn["text"]), callback_data=str(btn.get("callback_data", "")))
        for btn in row
        if isinstance(btn, dict)
    ]


@dataclass(frozen=True, slots=True)
class FileData:
    """Binary payload attached to an outgoing Telegram API call."""

    data: bytes
    filename: str = ""
    content_type: str = "application/octet-stream"


@dataclass(frozen=True, slots=True)
class TelegramApiCall:
    """Record of a single outgoing Telegram Bot API call."""

    api_method: str
    parameters: dict[str, str]
    file: FileData | None = None
    result: JsonValue | None = None


@dataclass(slots=True)
class ServerlessMessage:
    """Response from the serverless client, mimicking Telethon's Message.

    Properties (.photo, .document, .voice, .video_note, .file) return real
    Telethon TL types so that test assertions are identical across backends.
    """

    id: int = 0
    text: str = ""
    media_photo: Photo | None = None
    media_document: Document | None = None
    invoice_data: MessageMediaInvoice | None = None
    raw_bytes: bytes = b""
    file_store: dict[str, FileData] = field(default_factory=dict, repr=False)
    response_file_id: str = ""
    reply_markup_data: ReplyMarkup | None = field(default=None, repr=False)
    _click_callback: ClickCallback | None = field(default=None, repr=False)
    _file_cache: TelethonFile | None = field(default=None, repr=False)

    @property
    def photo(self) -> Photo | None:
        """The Photo media in this message, if any."""
        return self.media_photo

    @property
    def document(self) -> Document | None:
        """The Document media (plain document, not voice/video_note)."""
        if self.media_document is None:
            return None
        for attr in self.media_document.attributes:
            if isinstance(attr, DocumentAttributeAudio) and attr.voice:
                return None
            if isinstance(attr, DocumentAttributeVideo) and attr.round_message:
                return None
        return self.media_document

    @property
    def voice(self) -> Document | None:
        """The Document media if it is a voice note."""
        if self.media_document is None:
            return None
        for attr in self.media_document.attributes:
            if isinstance(attr, DocumentAttributeAudio) and attr.voice:
                return self.media_document
        return None

    @property
    def video_note(self) -> Document | None:
        """The Document media if it is a video note (round message)."""
        if self.media_document is None:
            return None
        for attr in self.media_document.attributes:
            if isinstance(attr, DocumentAttributeVideo) and attr.round_message:
                return self.media_document
        return None

    @property
    def file(self) -> TelethonFile | None:
        """Telethon File wrapper providing .size, .width, .height, .mime_type, .name."""
        if self._file_cache is None:
            media = self.media_photo or self.media_document
            if media:
                self._file_cache = TelethonFile(media)
        return self._file_cache

    @property
    def invoice(self) -> MessageMediaInvoice | None:
        """Invoice details if this is a payment request."""
        return self.invoice_data

    @property
    def buttons(self) -> list[list[ServerlessButton]] | None:
        """Keyboard button rows, matching Telethon's ``message.buttons`` layout.

        Works for both ``inline_keyboard`` and ``keyboard`` reply-markup types.
        Returns *None* when no markup is present.
        """
        if self.reply_markup_data is None:
            return None
        for key in ("inline_keyboard", "keyboard"):
            rows = self.reply_markup_data.get(key)
            if isinstance(rows, list):
                return [_wrap_button_row(row) for row in rows]
        return None

    @property
    def button_count(self) -> int:
        """Total number of buttons across all rows."""
        rows = self.buttons
        if rows is None:
            return 0
        return sum(len(row) for row in rows)

    async def download_media(self, file: type = bytes) -> bytes | None:
        """Download media bytes, matching Telethon's Message.download_media(file=bytes).

        Returns raw bytes from the bot's response (for uploads like mirror)
        or from the in-memory file store (for echo/passthrough).
        """
        del file  # always returns bytes in serverless mode
        if self.raw_bytes:
            return self.raw_bytes
        if self.response_file_id and self.response_file_id in self.file_store:
            return self.file_store[self.response_file_id].data
        return None

    async def click(self, *, data: bytes) -> "ServerlessMessage":
        """Simulate pressing an inline button, matching Telethon's ``message.click(data=...)``.

        Delegates to the parent client's callback-query handler.
        """
        if self._click_callback is None:
            raise RuntimeError("click() requires a client reference (_click_callback).")
        return await self._click_callback(self.id, data.decode())
