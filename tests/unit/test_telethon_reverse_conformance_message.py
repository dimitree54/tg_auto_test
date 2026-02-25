"""Reverse conformance tests for Telethon Message.

Tests that every public method/attribute on real Telethon Message also exists on our fake class.
These tests will xfail for missing members until T5 adds the necessary stubs.
"""

import pytest
from telethon.tl.custom.message import Message

from tg_auto_test.test_utils.serverless_message import ServerlessMessage


def _get_public_members(cls: type) -> set[str]:
    """Return set of public member names (not starting with '_')."""
    return {name for name in dir(cls) if not name.startswith("_")}


# Members we intentionally skip because they're protocol-internal or not applicable
_MESSAGE_ALLOWLIST = {
    "CONSTRUCTOR_ID",  # TL protocol constant, not needed for testing interface
    "SUBCLASS_OF_ID",  # TL protocol constant, not needed for testing interface
    "from_reader",  # TL protocol deserialization, not applicable to serverless testing
    "serialize_bytes",  # TL protocol serialization, not applicable to serverless testing
    "serialize_datetime",  # TL protocol serialization helper, not applicable to serverless testing
    "to_dict",  # TL protocol serialization, not applicable to serverless testing
    "to_json",  # TL protocol serialization, not applicable to serverless testing
    "stringify",  # TL protocol debugging, not applicable to serverless testing
    "pretty_format",  # TL protocol debugging, not applicable to serverless testing
    "client",  # Reference to TelegramClient instance, handled differently in serverless
    "input_chat",  # Chat entity resolution, handled differently in serverless
    "input_sender",  # Sender entity resolution, handled differently in serverless
    "is_channel",  # Chat type check, handled differently in serverless
    "is_group",  # Chat type check, handled differently in serverless
    "is_private",  # Chat type check, handled differently in serverless
    "get_chat",  # Async chat entity fetch, not applicable to serverless testing
    "get_input_chat",  # Async input chat fetch, not applicable to serverless testing
    "get_input_sender",  # Async input sender fetch, not applicable to serverless testing
    "get_sender",  # Async sender fetch, not applicable to serverless testing
    "respond",  # Message response method, not applicable to serverless testing
    "get_entities_text",  # Entity text extraction, complex feature not needed for basic testing
    "get_buttons",  # Button matrix access, handled differently in serverless
    "mark_read",  # Mark message as read, not applicable to serverless testing
    "pin",  # Pin message method, not applicable to serverless testing
    "unpin",  # Unpin message method, not applicable to serverless testing
}

# Members that already exist on our ServerlessMessage class (should not be marked xfail)
_MESSAGE_IMPLEMENTED_MEMBERS = {
    "audio",
    "button_count",
    "buttons",
    "chat",
    "chat_id",
    "click",
    "contact",
    "delete",
    "dice",
    "document",
    "download_media",
    "edit",
    "file",
    "forward",
    "forward_to",
    "game",
    "get_reply_message",
    "gif",
    "invoice",
    "photo",
    "poll",
    "raw_text",
    "reply",
    "reply_to_msg_id",
    "sender",
    "sender_id",
    "sticker",
    "text",
    "venue",
    "via_bot",
    "video",
    "video_note",
    "voice",
    "web_preview",
}


class TestMessageReverseConformance:
    """Test that our ServerlessMessage class has all public methods/attributes from Message."""

    ALLOWLIST = _MESSAGE_ALLOWLIST
    IMPLEMENTED_MEMBERS = _MESSAGE_IMPLEMENTED_MEMBERS

    @pytest.mark.parametrize(
        "member_name",
        [
            pytest.param(
                member, marks=pytest.mark.xfail(strict=True) if member not in _MESSAGE_IMPLEMENTED_MEMBERS else ()
            )
            for member in sorted(_get_public_members(Message) - _MESSAGE_ALLOWLIST)
        ],
    )
    def test_member_exists(self, member_name: str) -> None:
        """Test that each Telethon Message public member exists on ServerlessMessage."""
        assert hasattr(ServerlessMessage, member_name), (
            f"Member '{member_name}' exists on Message but not on ServerlessMessage"
        )

    def test_allowlist_is_current(self) -> None:
        """Test that allowlist doesn't contain names that don't exist on Telethon Message."""
        telethon_members = _get_public_members(Message)
        stale_entries = self.ALLOWLIST - telethon_members

        assert not stale_entries, f"Allowlist contains entries that don't exist on Message: {stale_entries}"
