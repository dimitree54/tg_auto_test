"""Extended Telethon client interface conformance tests.

These tests verify additional client methods that should match Telethon signatures.
Known divergences are marked with pytest.mark.xfail(strict=True) so make check passes
while T3-T5 tasks fix the divergences.
"""

import inspect

from telethon import TelegramClient

from tg_auto_test.test_utils.serverless_telegram_client_core import ServerlessTelegramClientCore


class TestTelegramClientExtendedConformance:
    """Test additional client methods that should conform to TelegramClient interface."""

    def test_client_send_message_signature(self) -> None:
        """Test send_message() method signature matches Telethon."""
        telethon_sig = inspect.signature(TelegramClient.send_message)

        assert hasattr(ServerlessTelegramClientCore, "send_message"), (
            "ServerlessTelegramClientCore missing send_message method"
        )

        our_sig = inspect.signature(ServerlessTelegramClientCore.send_message)
        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )

    def test_client_send_file_signature(self) -> None:
        """Test send_file() method signature matches Telethon."""
        telethon_sig = inspect.signature(TelegramClient.send_file)

        assert hasattr(ServerlessTelegramClientCore, "send_file"), (
            "ServerlessTelegramClientCore missing send_file method"
        )

        our_sig = inspect.signature(ServerlessTelegramClientCore.send_file)
        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )

    def test_client_download_media_signature(self) -> None:
        """Test download_media() method signature matches Telethon."""
        telethon_sig = inspect.signature(TelegramClient.download_media)

        assert hasattr(ServerlessTelegramClientCore, "download_media"), (
            "ServerlessTelegramClientCore missing download_media method"
        )

        our_sig = inspect.signature(ServerlessTelegramClientCore.download_media)
        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )

    def test_client_get_entity_signature(self) -> None:
        """Test get_entity() method signature matches Telethon."""
        telethon_sig = inspect.signature(TelegramClient.get_entity)

        assert hasattr(ServerlessTelegramClientCore, "get_entity"), (
            "ServerlessTelegramClientCore missing get_entity method"
        )

        our_sig = inspect.signature(ServerlessTelegramClientCore.get_entity)
        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )
