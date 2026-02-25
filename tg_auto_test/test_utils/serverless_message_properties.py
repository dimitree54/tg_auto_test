"""Mixin class for ServerlessMessage media properties."""

from telethon.tl.custom.file import File as TelethonFile
from telethon.tl.types import (
    Document,
    DocumentAttributeAudio,
    DocumentAttributeVideo,
    MessageMediaInvoice,
    MessageMediaPoll,
    Photo,
)

from tg_auto_test.test_utils.json_types import JsonValue
from tg_auto_test.test_utils.model_helpers import build_poll_media
from tg_auto_test.test_utils.serverless_button import ServerlessButton


def _wrap_button_row(row: JsonValue) -> list[ServerlessButton]:
    """Convert a raw JSON row of buttons into ServerlessButton objects."""
    if not isinstance(row, list):
        return []
    return [
        ServerlessButton(text=str(btn["text"]), _callback_data=str(btn.get("callback_data", "")))
        for btn in row
        if isinstance(btn, dict)
    ]


class ServerlessMessageProperties:
    """Mixin class containing media-related property methods for ServerlessMessage."""

    @property
    def photo(self) -> Photo | None:
        """The Photo media in this message, if any."""
        return self._media_photo

    @property
    def document(self) -> Document | None:
        """The Document media - returns Document for ALL document types including voice/video_note."""
        return self._media_document

    @property
    def voice(self) -> Document | None:
        """The Document media if it is a voice note."""
        if self._media_document is None:
            return None
        for attr in self._media_document.attributes:
            if isinstance(attr, DocumentAttributeAudio) and attr.voice:
                return self._media_document
        return None

    @property
    def video_note(self) -> Document | None:
        """The Document media if it is a video note (round message)."""
        if self._media_document is None:
            return None
        for attr in self._media_document.attributes:
            if isinstance(attr, DocumentAttributeVideo) and attr.round_message:
                return self._media_document
        return None

    @property
    def file(self) -> TelethonFile | None:
        """Telethon File wrapper providing .size, .width, .height, .mime_type, .name."""
        if self._file_cache is None:
            media = self._media_photo or self._media_document
            if media:
                self._file_cache = TelethonFile(media)
        return self._file_cache

    @property
    def invoice(self) -> MessageMediaInvoice | None:
        """Invoice details if this is a payment request."""
        return self._invoice_data

    @property
    def poll(self) -> MessageMediaPoll | None:
        """Poll details if this is a poll message."""
        return build_poll_media(self._poll_data)

    @property
    def buttons(self) -> list[list[ServerlessButton]] | None:
        """Keyboard button rows, matching Telethon's ``message.buttons`` layout.

        Works for both ``inline_keyboard`` and ``keyboard`` reply-markup types.
        Returns *None* when no markup is present.
        """
        if self._reply_markup_data is None:
            return None
        for key in ("inline_keyboard", "keyboard"):
            rows = self._reply_markup_data.get(key)
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
