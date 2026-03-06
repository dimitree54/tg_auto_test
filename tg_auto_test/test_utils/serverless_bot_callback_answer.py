"""ServerlessBotCallbackAnswer mimicking Telethon's BotCallbackAnswer."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ServerlessBotCallbackAnswer:
    """Mirrors ``telethon.tl.types.messages.BotCallbackAnswer``.

    Returned by ``ServerlessMessage.click(data=...)`` to match
    the real Telethon return type.
    """

    message: str = ""
    alert: bool = False
    has_url: bool = False
    url: str = ""
    cache_time: int = 0
