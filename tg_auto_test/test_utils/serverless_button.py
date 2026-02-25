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

    @property
    def client(self) -> object:
        raise NotImplementedError("client reference is not available in serverless mode")

    @property
    def inline_query(self) -> object:
        raise NotImplementedError("inline_query is not supported")

    @property
    def url(self) -> str:
        raise NotImplementedError("url is not supported")

    async def click(self, *args: object, **kwargs: object) -> object:
        del args, kwargs
        raise NotImplementedError("button-level click() is not supported in serverless mode")
