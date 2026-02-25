"""Reverse conformance tests for Telethon Conversation.

Tests that every public method/attribute on real Telethon Conversation also exists on our fake class.
These tests will xfail for missing members until T6 adds the necessary stubs.
"""

import pytest
from telethon.tl.custom.conversation import Conversation

from tg_auto_test.test_utils.serverless_telegram_conversation import ServerlessTelegramConversation


def _get_public_members(cls: type) -> set[str]:
    """Return set of public member names (not starting with '_')."""
    return {name for name in dir(cls) if not name.startswith("_")}


# Members we intentionally skip because they're not applicable to serverless testing
_CONVERSATION_ALLOWLIST = {
    "chat",  # Chat entity reference, handled differently in serverless
    "chat_id",  # Chat ID access, handled differently in serverless
    "input_chat",  # Input chat entity, handled differently in serverless
    "get_chat",  # Async chat fetch, not applicable to serverless testing
    "get_input_chat",  # Async input chat fetch, not applicable to serverless testing
    "is_channel",  # Chat type check, not applicable to serverless testing
    "is_group",  # Chat type check, not applicable to serverless testing
    "is_private",  # Chat type check, not applicable to serverless testing
}

# Members that already exist on our conversation class (should not be marked xfail)
_CONVERSATION_IMPLEMENTED_MEMBERS = {
    "cancel",
    "cancel_all",
    "get_edit",
    "get_reply",
    "get_response",
    "mark_read",
    "send_file",
    "send_message",
    "wait_event",
    "wait_read",
}


class TestConversationReverseConformance:
    """Test that our ServerlessTelegramConversation class has all public methods/attributes from Conversation."""

    ALLOWLIST = _CONVERSATION_ALLOWLIST
    IMPLEMENTED_MEMBERS = _CONVERSATION_IMPLEMENTED_MEMBERS

    @pytest.mark.parametrize(
        "member_name",
        [
            pytest.param(
                member, marks=pytest.mark.xfail(strict=True) if member not in _CONVERSATION_IMPLEMENTED_MEMBERS else ()
            )
            for member in sorted(_get_public_members(Conversation) - _CONVERSATION_ALLOWLIST)
        ],
    )
    def test_member_exists(self, member_name: str) -> None:
        """Test that each Telethon Conversation public member exists on ServerlessTelegramConversation."""
        assert hasattr(ServerlessTelegramConversation, member_name), (
            f"Member '{member_name}' exists on Conversation but not on ServerlessTelegramConversation"
        )

    def test_allowlist_is_current(self) -> None:
        """Test that allowlist doesn't contain names that don't exist on Telethon Conversation."""
        telethon_members = _get_public_members(Conversation)
        stale_entries = self.ALLOWLIST - telethon_members

        assert not stale_entries, f"Allowlist contains entries that don't exist on Conversation: {stale_entries}"
