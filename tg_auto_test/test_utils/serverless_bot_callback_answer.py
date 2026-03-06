"""ServerlessBotCallbackAnswer class for Telegram bot testing infrastructure."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ServerlessBotCallbackAnswer:
    """Mimics Telethon's BotCallbackAnswer, returned by Message.click().

    In Telethon, clicking an inline button sends a callback query and returns a
    BotCallbackAnswer (the bot's answer to the query). Any messages the bot sends
    during callback processing remain available via conv.get_response().

    This class matches that behaviour: click() returns a BotCallbackAnswer-like
    object and does NOT consume bot response messages from the outbox.
    """

    message: str = ""
    alert: bool = False
    has_url: bool = False
    url: str = ""
    cache_time: int = 0
