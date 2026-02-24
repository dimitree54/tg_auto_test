"""Extended Telethon message interface conformance tests.

These tests verify additional message methods and properties that should match Telethon.
Known divergences are marked with pytest.mark.xfail(strict=True) so make check passes
while T3-T5 tasks fix the divergences.
"""

import inspect

import pytest
from telethon.tl.custom.message import Message

from tg_auto_test.test_utils.models import ServerlessMessage


class TestMessageExtendedConformance:
    """Test additional message methods that should conform to Telethon Message interface."""

    @pytest.mark.xfail(strict=True, reason="Divergence: missing delete method")
    def test_message_delete_signature(self) -> None:
        """Test Message.delete() signature matches Telethon."""
        telethon_sig = inspect.signature(Message.delete)

        assert hasattr(ServerlessMessage, "delete"), "ServerlessMessage missing delete method"

        our_sig = inspect.signature(ServerlessMessage.delete)
        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )

    @pytest.mark.xfail(strict=True, reason="Divergence: missing edit method")
    def test_message_edit_signature(self) -> None:
        """Test Message.edit() signature matches Telethon."""
        telethon_sig = inspect.signature(Message.edit)

        assert hasattr(ServerlessMessage, "edit"), "ServerlessMessage missing edit method"

        our_sig = inspect.signature(ServerlessMessage.edit)
        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )

    @pytest.mark.xfail(strict=True, reason="Divergence: missing reply method")
    def test_message_reply_signature(self) -> None:
        """Test Message.reply() signature matches Telethon."""
        telethon_sig = inspect.signature(Message.reply)

        assert hasattr(ServerlessMessage, "reply"), "ServerlessMessage missing reply method"

        our_sig = inspect.signature(ServerlessMessage.reply)
        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )

    @pytest.mark.xfail(strict=True, reason="Divergence: missing forward_to method")
    def test_message_forward_to_signature(self) -> None:
        """Test Message.forward_to() signature matches Telethon."""
        telethon_sig = inspect.signature(Message.forward_to)

        assert hasattr(ServerlessMessage, "forward_to"), "ServerlessMessage missing forward_to method"

        our_sig = inspect.signature(ServerlessMessage.forward_to)
        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )

    @pytest.mark.xfail(strict=True, reason="Divergence: missing message properties")
    def test_message_additional_properties(self) -> None:
        """Test that additional message properties exist."""
        # Properties that should exist on our message class
        expected_properties = {
            "sender",
            "sender_id",
            "chat",
            "chat_id",
            "date",
            "raw_text",
            "reply_to_msg_id",
            "forward",
            "via_bot",
            "media",
            "sticker",
            "contact",
            "location",
            "venue",
            "audio",
            "voice",
            "video",
            "video_note",
            "gif",
            "game",
            "web_preview",
            "dice",
        }

        for prop in expected_properties:
            if hasattr(Message, prop):
                assert hasattr(ServerlessMessage, prop), f"ServerlessMessage missing property: {prop}"

    @pytest.mark.xfail(strict=True, reason="Divergence: missing get_reply_message method")
    def test_message_get_reply_message_signature(self) -> None:
        """Test Message.get_reply_message() signature matches Telethon."""
        telethon_sig = inspect.signature(Message.get_reply_message)

        assert hasattr(ServerlessMessage, "get_reply_message"), "ServerlessMessage missing get_reply_message method"

        our_sig = inspect.signature(ServerlessMessage.get_reply_message)
        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )
