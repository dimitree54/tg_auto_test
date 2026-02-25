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
_MESSAGE_ALLOWLIST = set()

# Members that already exist on our ServerlessMessage class (should not be marked xfail)
_MESSAGE_IMPLEMENTED_MEMBERS = {
    "CONSTRUCTOR_ID",
    "SUBCLASS_OF_ID",
    "action_entities",
    "audio",
    "button_count",
    "buttons",
    "chat",
    "chat_id",
    "click",
    "client",
    "contact",
    "delete",
    "dice",
    "document",
    "download_media",
    "edit",
    "file",
    "forward",
    "forward_to",
    "from_reader",
    "game",
    "geo",
    "get_buttons",
    "get_chat",
    "get_entities_text",
    "get_input_chat",
    "get_input_sender",
    "get_reply_message",
    "get_sender",
    "gif",
    "input_chat",
    "input_sender",
    "invoice",
    "is_channel",
    "is_group",
    "is_private",
    "is_reply",
    "mark_read",
    "photo",
    "pin",
    "poll",
    "pretty_format",
    "raw_text",
    "reply",
    "reply_to_chat",
    "reply_to_msg_id",
    "reply_to_sender",
    "respond",
    "sender",
    "sender_id",
    "serialize_bytes",
    "serialize_datetime",
    "sticker",
    "stringify",
    "text",
    "to_dict",
    "to_id",
    "to_json",
    "unpin",
    "venue",
    "via_bot",
    "via_input_bot",
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
