"""Mixin class for ServerlessMessage metadata properties."""


class ServerlessMessageMetadata:
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
