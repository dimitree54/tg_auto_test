"""Mixin class for ServerlessMessage metadata properties."""

from tg_auto_test.test_utils.serverless_message_serial_stubs import ServerlessMessageSerialStubs


class ServerlessMessageMetadata(ServerlessMessageSerialStubs):
    """Mixin class containing metadata-related property methods for ServerlessMessage."""

    @property
    def sender(self) -> object:
        """The sender entity - raises NotImplementedError since entity resolution is not supported."""
        raise NotImplementedError("sender requires entity resolution")

    @property
    def sender_id(self) -> int | None:
        """The sender ID."""
        return self._sender_id

    @property
    def chat(self) -> object:
        """The chat entity - raises NotImplementedError since entity resolution is not supported."""
        raise NotImplementedError("chat requires entity resolution")

    @property
    def chat_id(self) -> int | None:
        """The chat ID."""
        return self._chat_id_value

    @property
    def raw_text(self) -> str:
        """The raw text of the message."""
        return self.text

    @property
    def reply_to_msg_id(self) -> int | None:
        """The ID of the message this message is replying to."""
        return None

    @property
    def forward(self) -> None:
        """Forward information - not supported."""
        return None

    @property
    def via_bot(self) -> None:
        """Via bot information - not supported."""
        return None

    @property
    def sticker(self) -> None:
        """Sticker media - not supported."""
        return None

    @property
    def contact(self) -> None:
        """Contact media - not supported."""
        return None

    @property
    def venue(self) -> None:
        """Venue media - not supported."""
        return None

    @property
    def gif(self) -> None:
        """GIF media - not supported."""
        return None

    @property
    def game(self) -> None:
        """Game media - not supported."""
        return None

    @property
    def web_preview(self) -> None:
        """Web preview information - not supported."""
        return None

    @property
    def dice(self) -> None:
        """Dice media - not supported."""
        return None

    @property
    def action_entities(self) -> None:
        """Action entities - not supported in serverless testing mode."""
        raise NotImplementedError("action_entities is not supported in serverless testing mode")

    @property
    def geo(self) -> None:
        """Geographic location - not supported in serverless testing mode."""
        raise NotImplementedError("geo is not supported in serverless testing mode")

    @property
    def is_reply(self) -> bool:
        """Whether this message is a reply - not supported in serverless testing mode."""
        raise NotImplementedError("is_reply is not supported in serverless testing mode")

    @property
    def reply_to_chat(self) -> None:
        """Chat being replied to - not supported in serverless testing mode."""
        raise NotImplementedError("reply_to_chat is not supported in serverless testing mode")

    @property
    def reply_to_sender(self) -> None:
        """Sender being replied to - not supported in serverless testing mode."""
        raise NotImplementedError("reply_to_sender is not supported in serverless testing mode")

    @property
    def to_id(self) -> None:
        """Legacy chat ID property - not supported in serverless testing mode."""
        raise NotImplementedError("to_id is not supported in serverless testing mode")

    @property
    def via_input_bot(self) -> None:
        """Via bot input entity - not supported in serverless testing mode."""
        raise NotImplementedError("via_input_bot is not supported in serverless testing mode")

    @property
    def client(self) -> None:
        """Reference to TelegramClient instance - not supported in serverless testing mode."""
        raise NotImplementedError("client is not supported in serverless testing mode")

    @property
    def input_chat(self) -> None:
        """Chat entity resolution - not supported in serverless testing mode."""
        raise NotImplementedError("input_chat is not supported in serverless testing mode")

    @property
    def input_sender(self) -> None:
        """Sender entity resolution - not supported in serverless testing mode."""
        raise NotImplementedError("input_sender is not supported in serverless testing mode")

    @property
    def is_channel(self) -> bool:
        """Chat type check - not supported in serverless testing mode."""
        raise NotImplementedError("is_channel is not supported in serverless testing mode")

    @property
    def is_group(self) -> bool:
        """Chat type check - not supported in serverless testing mode."""
        raise NotImplementedError("is_group is not supported in serverless testing mode")

    @property
    def is_private(self) -> bool:
        """Chat type check - not supported in serverless testing mode."""
        raise NotImplementedError("is_private is not supported in serverless testing mode")
