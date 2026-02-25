"""ServerlessButton class for Telegram bot testing infrastructure."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ServerlessButton:
    """Wraps a raw button dict to expose a ``.text`` attribute like Telethon."""

    text: str
    _callback_data: str = ""

    @property
    def data(self) -> bytes:
        """Button callback data as bytes, matching Telethon MessageButton.data."""
        return self._callback_data.encode("utf-8")
