"""Reverse conformance tests for Telethon TelegramClient.

Tests that every public method/attribute on real Telethon TelegramClient also exists on our fake classes.
These tests will xfail for missing members until T4 adds the necessary stubs.
"""

import pytest
from telethon import TelegramClient

from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient
from tg_auto_test.test_utils.serverless_telegram_client_core import ServerlessTelegramClientCore


def _get_public_members(cls: type) -> set[str]:
    """Return set of public member names (not starting with '_')."""
    return {name for name in dir(cls) if not name.startswith("_")}


# Members we intentionally skip because they're not applicable to serverless testing
_CLIENT_ALLOWLIST = {
    "flood_sleep_threshold",  # Rate limiting attribute, not applicable to serverless testing
    "loop",  # Event loop reference, not applicable to serverless testing
    "parse_mode",  # Global parse mode setting, handled differently in serverless
    "is_bot",  # Connection type flag, determined differently in serverless
    "is_connected",  # Connection state, handled differently in serverless
    "is_user_authorized",  # Auth state, not applicable to serverless testing
}

# Members that already exist on our client classes (should not be marked xfail)
_CLIENT_IMPLEMENTED_MEMBERS = {
    "connect",
    "conversation",
    "disconnect",
    "download_media",
    "get_dialogs",
    "get_entity",
    "get_input_entity",
    "get_me",
    "get_messages",
    "send_file",
    "send_message",
}


class TestTelegramClientReverseConformance:
    """Test that our client classes have all public methods/attributes from TelegramClient."""

    ALLOWLIST = _CLIENT_ALLOWLIST
    IMPLEMENTED_MEMBERS = _CLIENT_IMPLEMENTED_MEMBERS

    @pytest.mark.parametrize(
        "member_name",
        [
            pytest.param(
                member, marks=pytest.mark.xfail(strict=True) if member not in _CLIENT_IMPLEMENTED_MEMBERS else ()
            )
            for member in sorted(_get_public_members(TelegramClient) - _CLIENT_ALLOWLIST)
        ],
    )
    def test_member_exists(self, member_name: str) -> None:
        """Test that each Telethon public member exists on our client classes."""
        # Check both core and extended client classes since some methods live on subclass
        has_core = hasattr(ServerlessTelegramClientCore, member_name)
        has_extended = hasattr(ServerlessTelegramClient, member_name)

        assert has_core or has_extended, (
            f"Member '{member_name}' exists on TelegramClient but not on "
            f"ServerlessTelegramClientCore or ServerlessTelegramClient"
        )

    def test_allowlist_is_current(self) -> None:
        """Test that allowlist doesn't contain names that don't exist on Telethon."""
        telethon_members = _get_public_members(TelegramClient)
        stale_entries = self.ALLOWLIST - telethon_members

        assert not stale_entries, f"Allowlist contains entries that don't exist on TelegramClient: {stale_entries}"
