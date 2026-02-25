"""Basic Telethon client interface conformance tests.

These tests verify that our serverless client classes match the real Telethon 1.42 TelegramClient signatures.
Known divergences are marked with pytest.mark.xfail(strict=True) so make check passes
while T3-T5 tasks fix the divergences.
"""

import inspect

from telethon import TelegramClient

from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient
from tg_auto_test.test_utils.serverless_telegram_client_core import ServerlessTelegramClientCore


class TestTelegramClientConformance:
    """Test that our client classes conform to TelegramClient interface."""

    def test_conversation_signature(self) -> None:
        """Test conversation() method signature matches Telethon."""
        telethon_sig = inspect.signature(TelegramClient.conversation)
        our_sig = inspect.signature(ServerlessTelegramClientCore.conversation)

        # Compare parameter names, kinds, and defaults
        telethon_params = telethon_sig.parameters
        our_params = our_sig.parameters

        # Skip 'self' parameter
        telethon_param_names = [name for name in telethon_params.keys() if name != "self"]
        our_param_names = [name for name in our_params.keys() if name != "self"]

        assert telethon_param_names == our_param_names, (
            f"Parameter names mismatch: Telethon {telethon_param_names} vs Ours {our_param_names}"
        )

        # Check parameter kinds and defaults
        for name in telethon_param_names:
            telethon_param = telethon_params[name]
            our_param = our_params[name]

            assert telethon_param.kind == our_param.kind, (
                f"Parameter '{name}' kind mismatch: Telethon {telethon_param.kind} vs Ours {our_param.kind}"
            )

            assert telethon_param.default == our_param.default, (
                f"Parameter '{name}' default mismatch: Telethon {telethon_param.default} vs Ours {our_param.default}"
            )

    def test_get_messages_signature(self) -> None:
        """Test get_messages() method signature matches Telethon."""
        telethon_sig = inspect.signature(TelegramClient.get_messages)
        our_sig = inspect.signature(ServerlessTelegramClientCore.get_messages)

        # Compare parameter names, kinds, and defaults (excluding 'self')
        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )

        for name in telethon_params:
            telethon_param = telethon_params[name]
            our_param = our_params[name]

            assert telethon_param.kind == our_param.kind, (
                f"Parameter '{name}' kind mismatch: Telethon {telethon_param.kind} vs Ours {our_param.kind}"
            )

    def test_get_me_signature(self) -> None:
        """Test get_me() method signature matches Telethon."""
        telethon_sig = inspect.signature(TelegramClient.get_me)
        our_sig = inspect.signature(ServerlessTelegramClientCore.get_me)

        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )

    def test_get_input_entity_signature(self) -> None:
        """Test get_input_entity() method signature matches Telethon."""
        telethon_sig = inspect.signature(TelegramClient.get_input_entity)
        our_sig = inspect.signature(ServerlessTelegramClient.get_input_entity)

        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )

    def test_get_dialogs_signature(self) -> None:
        """Test get_dialogs() method signature matches Telethon."""
        telethon_sig = inspect.signature(TelegramClient.get_dialogs)
        our_sig = inspect.signature(ServerlessTelegramClientCore.get_dialogs)

        telethon_params = {name: param for name, param in telethon_sig.parameters.items() if name != "self"}
        our_params = {name: param for name, param in our_sig.parameters.items() if name != "self"}

        # Should have matching parameters
        assert list(telethon_params.keys()) == list(our_params.keys()), (
            f"Parameter names mismatch: Telethon {list(telethon_params.keys())} vs Ours {list(our_params.keys())}"
        )

    def test_connect_signature(self) -> None:
        """Test connect() method signature matches Telethon."""
        telethon_sig = inspect.signature(TelegramClient.connect)
        our_sig = inspect.signature(ServerlessTelegramClientCore.connect)

        telethon_params = list(telethon_sig.parameters.keys())
        our_params = list(our_sig.parameters.keys())

        # Both should only have 'self' parameter
        assert telethon_params == our_params == ["self"]

    def test_disconnect_signature(self) -> None:
        """Test disconnect() method signature matches Telethon."""
        telethon_sig = inspect.signature(TelegramClient.disconnect)
        our_sig = inspect.signature(ServerlessTelegramClientCore.disconnect)

        telethon_params = list(telethon_sig.parameters.keys())
        our_params = list(our_sig.parameters.keys())

        # Both should only have 'self' parameter
        assert telethon_params == our_params == ["self"]

    def test_no_extra_public_methods(self) -> None:
        """Test that our client has no extra public methods beyond Telethon's."""
        telethon_methods = {
            name for name in dir(TelegramClient) if not name.startswith("_") and callable(getattr(TelegramClient, name))
        }
        our_methods = {
            name
            for name in dir(ServerlessTelegramClientCore)
            if not name.startswith("_") and callable(getattr(ServerlessTelegramClientCore, name))
        }

        # Allow our methods that are documented public API
        allowed_extra_methods = {"pop_response"}  # Demo UI compatibility method

        extra_methods = our_methods - telethon_methods - allowed_extra_methods
        assert not extra_methods, f"Extra public methods found: {extra_methods}"

    def test_no_extra_public_attributes(self) -> None:
        """Test that our client has no extra public attributes beyond Telethon's."""
        # Get public attributes from our class (excluding properties which are valid)
        core_attrs = {
            name
            for name in dir(ServerlessTelegramClientCore)
            if not name.startswith("_")
            and not callable(getattr(ServerlessTelegramClientCore, name))
            and not isinstance(getattr(ServerlessTelegramClientCore, name), property)
        }

        # Should be empty - all attributes should be private or properties
        assert not core_attrs, f"Found public attributes that should be private: {core_attrs}"
