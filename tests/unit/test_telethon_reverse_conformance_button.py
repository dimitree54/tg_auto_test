"""Reverse conformance tests for Telethon MessageButton.

Tests that every public method/attribute on real Telethon MessageButton also exists on our fake class.
These tests will xfail for missing members until T6 adds the necessary stubs.
"""

import pytest
from telethon.tl.custom.messagebutton import MessageButton

from tg_auto_test.test_utils.serverless_button import ServerlessButton


def _get_public_members(cls: type) -> set[str]:
    """Return set of public member names (not starting with '_')."""
    return {name for name in dir(cls) if not name.startswith("_")}


# Members we intentionally skip because they're not applicable to serverless testing
_BUTTON_ALLOWLIST: set[str] = set()

# Members that already exist on our ServerlessButton class (should not be marked xfail)
_BUTTON_IMPLEMENTED_MEMBERS = {"click", "client", "data", "inline_query", "text", "url"}


class TestMessageButtonReverseConformance:
    """Test that our ServerlessButton class has all public methods/attributes from MessageButton."""

    ALLOWLIST = _BUTTON_ALLOWLIST
    IMPLEMENTED_MEMBERS = _BUTTON_IMPLEMENTED_MEMBERS

    @pytest.mark.parametrize(
        "member_name",
        [
            pytest.param(
                member, marks=pytest.mark.xfail(strict=True) if member not in _BUTTON_IMPLEMENTED_MEMBERS else ()
            )
            for member in sorted(_get_public_members(MessageButton) - _BUTTON_ALLOWLIST)
        ],
    )
    def test_member_exists(self, member_name: str) -> None:
        """Test that each Telethon MessageButton public member exists on ServerlessButton."""
        assert hasattr(ServerlessButton, member_name), (
            f"Member '{member_name}' exists on MessageButton but not on ServerlessButton"
        )

    def test_allowlist_is_current(self) -> None:
        """Test that allowlist doesn't contain names that don't exist on Telethon MessageButton."""
        telethon_members = _get_public_members(MessageButton)
        stale_entries = self.ALLOWLIST - telethon_members

        assert not stale_entries, f"Allowlist contains entries that don't exist on MessageButton: {stale_entries}"
