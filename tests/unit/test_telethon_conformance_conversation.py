"""Telethon conversation interface conformance tests.

These tests verify that our ServerlessTelegramConversation matches the real Telethon Conversation interface.
"""

import inspect

from telethon.tl.custom.conversation import Conversation

from tg_auto_test.test_utils.serverless_telegram_conversation import ServerlessTelegramConversation


class TestConversationConformance:
    """Test that ServerlessTelegramConversation conforms to Conversation interface."""

    def test_conversation_send_message_exists(self) -> None:
        """Test that send_message method exists (pass-through)."""
        assert hasattr(Conversation, "send_message")
        assert hasattr(ServerlessTelegramConversation, "send_message")

    def test_conversation_send_file_exists(self) -> None:
        """Test that send_file method exists (pass-through)."""
        assert hasattr(Conversation, "send_file")
        assert hasattr(ServerlessTelegramConversation, "send_file")

    def test_conversation_get_response_signature(self) -> None:
        """Test get_response() signature matches Telethon."""
        telethon_sig = inspect.signature(Conversation.get_response)
        our_sig = inspect.signature(ServerlessTelegramConversation.get_response)

        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )

    def test_conversation_get_edit_signature(self) -> None:
        """Test get_edit() signature matches Telethon."""
        telethon_sig = inspect.signature(Conversation.get_edit)

        # Our implementation should have this method
        assert hasattr(ServerlessTelegramConversation, "get_edit"), (
            "ServerlessTelegramConversation missing get_edit method"
        )

        our_sig = inspect.signature(ServerlessTelegramConversation.get_edit)
        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )

    def test_conversation_get_reply_signature(self) -> None:
        """Test get_reply() signature matches Telethon."""
        telethon_sig = inspect.signature(Conversation.get_reply)

        # Our implementation should have this method
        assert hasattr(ServerlessTelegramConversation, "get_reply"), (
            "ServerlessTelegramConversation missing get_reply method"
        )

        our_sig = inspect.signature(ServerlessTelegramConversation.get_reply)
        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )

    def test_conversation_cancel_method(self) -> None:
        """Test that cancel() method exists."""
        assert hasattr(Conversation, "cancel")
        assert hasattr(ServerlessTelegramConversation, "cancel"), "ServerlessTelegramConversation missing cancel method"

    def test_conversation_cancel_all_method(self) -> None:
        """Test that cancel_all() method exists."""
        assert hasattr(Conversation, "cancel_all")
        assert hasattr(ServerlessTelegramConversation, "cancel_all"), (
            "ServerlessTelegramConversation missing cancel_all method"
        )

    def test_conversation_wait_event_signature(self) -> None:
        """Test wait_event() signature matches Telethon."""
        telethon_sig = inspect.signature(Conversation.wait_event)

        assert hasattr(ServerlessTelegramConversation, "wait_event"), (
            "ServerlessTelegramConversation missing wait_event method"
        )

        our_sig = inspect.signature(ServerlessTelegramConversation.wait_event)
        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )

    def test_conversation_wait_read_signature(self) -> None:
        """Test wait_read() signature matches Telethon."""
        telethon_sig = inspect.signature(Conversation.wait_read)

        assert hasattr(ServerlessTelegramConversation, "wait_read"), (
            "ServerlessTelegramConversation missing wait_read method"
        )

        our_sig = inspect.signature(ServerlessTelegramConversation.wait_read)
        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )

    def test_conversation_mark_read_signature(self) -> None:
        """Test mark_read() signature matches Telethon."""
        telethon_sig = inspect.signature(Conversation.mark_read)

        assert hasattr(ServerlessTelegramConversation, "mark_read"), (
            "ServerlessTelegramConversation missing mark_read method"
        )

        our_sig = inspect.signature(ServerlessTelegramConversation.mark_read)
        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )

    def test_no_extra_public_methods(self) -> None:
        """Test that ServerlessTelegramConversation has no extra public methods beyond Conversation."""
        telethon_methods = {
            name for name in dir(Conversation) if not name.startswith("_") and callable(getattr(Conversation, name))
        }
        our_methods = {
            name
            for name in dir(ServerlessTelegramConversation)
            if not name.startswith("_") and callable(getattr(ServerlessTelegramConversation, name))
        }

        # Allow our methods that are documented public API
        allowed_extra_methods: set[str] = set()  # No extra methods allowed for Conversation

        extra_methods = our_methods - telethon_methods - allowed_extra_methods
        assert not extra_methods, f"Extra public methods found: {extra_methods}"

    def test_no_extra_public_attributes(self) -> None:
        """Test that ServerlessTelegramConversation has no extra public attributes beyond Conversation."""
        # Get public attributes from Telethon (excluding properties)
        telethon_attrs = {
            name
            for name in dir(Conversation)
            if not name.startswith("_")
            and not callable(getattr(Conversation, name))
            and not isinstance(getattr(Conversation, name), property)
        }

        # Get public attributes from our class (excluding properties)
        our_attrs = {
            name
            for name in dir(ServerlessTelegramConversation)
            if not name.startswith("_")
            and not callable(getattr(ServerlessTelegramConversation, name))
            and not isinstance(getattr(ServerlessTelegramConversation, name), property)
        }

        # Allow attributes that exist in Telethon or are specifically allowed extras
        allowed_extra_attrs: set[str] = set()  # No extra attributes allowed for Conversation

        extra_attrs = our_attrs - telethon_attrs - allowed_extra_attrs
        assert not extra_attrs, f"Extra public attributes found: {extra_attrs}"
