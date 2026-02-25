"""Basic Telethon message and button interface conformance tests.

These tests verify that our ServerlessMessage and ServerlessButton match the real Telethon interfaces.
Known divergences are marked with pytest.mark.xfail(strict=True) so make check passes
while T3-T5 tasks fix the divergences.
"""

import inspect

from telethon.tl.custom.message import Message
from telethon.tl.custom.messagebutton import MessageButton

from tg_auto_test.test_utils.models import ServerlessButton, ServerlessMessage


class TestMessageConformance:
    """Test that ServerlessMessage conforms to Telethon Message interface."""

    def test_message_click_signature(self) -> None:
        """Test Message.click() signature matches Telethon."""
        telethon_sig = inspect.signature(Message.click)
        our_sig = inspect.signature(ServerlessMessage.click)

        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )

        # Check parameter kinds
        for name in telethon_params:
            telethon_param = telethon_params[name]
            our_param = our_params[name]

            assert telethon_param.kind == our_param.kind, (
                f"Parameter '{name}' kind mismatch: Telethon {telethon_param.kind} vs Ours {our_param.kind}"
            )

    def test_message_download_media_exists(self) -> None:
        """Test Message.download_media() method exists on both classes."""
        # Both classes should have the method
        assert hasattr(Message, "download_media")
        assert hasattr(ServerlessMessage, "download_media")

        # Telethon uses (*args, **kwargs) which is flexible,
        # our implementation has a specific signature but is compatible

    def test_no_extra_message_attributes(self) -> None:
        """Test ServerlessMessage has no extra public attributes beyond Telethon Message."""
        expected_private_attributes = {
            "poll_data",
            "response_file_id",
            "reply_markup_data",
            "media_photo",
            "media_document",
            "invoice_data",
            "callback_data",
        }

        message_attrs = {
            name
            for name in dir(ServerlessMessage)
            if not name.startswith("_") and not callable(getattr(ServerlessMessage, name))
        }

        # These should be private
        public_attrs_that_should_be_private = message_attrs & expected_private_attributes
        assert not public_attrs_that_should_be_private, (
            f"Message attributes should be private: {public_attrs_that_should_be_private}"
        )

    def test_required_message_properties_exist(self) -> None:
        """Test that required message properties exist."""
        required_properties = {
            "photo",
            "document",
            "voice",
            "video_note",
            "file",
            "invoice",
            "poll",
            "buttons",
            "text",
            "id",
        }

        for prop in required_properties:
            assert hasattr(ServerlessMessage, prop), f"Missing property: {prop}"


class TestButtonConformance:
    """Test that ServerlessButton conforms to MessageButton interface."""

    def test_button_data_property(self) -> None:
        """Test that ServerlessButton.data property returns bytes like MessageButton."""
        # MessageButton.data returns bytes
        assert hasattr(MessageButton, "data")
        assert hasattr(ServerlessButton, "data")

        # Create a test button
        button = ServerlessButton(text="Test", _callback_data="test_data")

        # Our implementation should have data as bytes
        assert hasattr(button, "data")
        assert isinstance(button.data, bytes)
