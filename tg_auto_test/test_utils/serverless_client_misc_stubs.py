"""Miscellaneous stubs for ServerlessTelegramClient.

This module provides NotImplementedError-raising stubs for Telethon event handling,
utility, and other miscellaneous methods that are not supported in serverless testing mode.
"""

from tg_auto_test.test_utils.serverless_client_query_api import ServerlessClientQueryAPI


class ServerlessClientMiscStubs(ServerlessClientQueryAPI):
    """Mixin providing miscellaneous stubs for ServerlessTelegramClient."""

    async def action(self, *args, **kwargs) -> object:
        """Send typing/action status. Not supported in serverless testing mode."""
        raise NotImplementedError("action() is not supported in serverless testing mode")

    def add_event_handler(self, *args, **kwargs) -> None:
        """Add event handler. Not supported in serverless testing mode."""
        raise NotImplementedError("add_event_handler() is not supported in serverless testing mode")

    def remove_event_handler(self, *args, **kwargs) -> None:
        """Remove event handler. Not supported in serverless testing mode."""
        raise NotImplementedError("remove_event_handler() is not supported in serverless testing mode")

    def list_event_handlers(self, *args, **kwargs) -> list:
        """List registered event handlers. Not supported in serverless testing mode."""
        raise NotImplementedError("list_event_handlers() is not supported in serverless testing mode")

    def on(self, *args, **kwargs) -> object:
        """Event handler decorator. Not supported in serverless testing mode."""
        raise NotImplementedError("on() is not supported in serverless testing mode")

    def build_reply_markup(self, *args, **kwargs) -> object:
        """Build reply markup from buttons. Not supported in serverless testing mode."""
        raise NotImplementedError("build_reply_markup() is not supported in serverless testing mode")

    async def catch_up(self, *args, **kwargs) -> None:
        """Catch up with missed updates. Not supported in serverless testing mode."""
        raise NotImplementedError("catch_up() is not supported in serverless testing mode")

    async def delete_dialog(self, *args, **kwargs) -> object:
        """Delete dialog/conversation. Not supported in serverless testing mode."""
        raise NotImplementedError("delete_dialog() is not supported in serverless testing mode")

    async def edit_folder(self, *args, **kwargs) -> object:
        """Edit chat folder. Not supported in serverless testing mode."""
        raise NotImplementedError("edit_folder() is not supported in serverless testing mode")

    async def end_takeout(self, *args, **kwargs) -> bool:
        """End takeout session. Not supported in serverless testing mode."""
        raise NotImplementedError("end_takeout() is not supported in serverless testing mode")

    def get_peer_id(self, *args, **kwargs) -> int:
        """Get peer ID from entity. Not supported in serverless testing mode."""
        raise NotImplementedError("get_peer_id() is not supported in serverless testing mode")

    async def inline_query(self, *args, **kwargs) -> object:
        """Send inline query. Not supported in serverless testing mode."""
        raise NotImplementedError("inline_query() is not supported in serverless testing mode")

    async def takeout(self, *args, **kwargs) -> object:
        """Start takeout session. Not supported in serverless testing mode."""
        raise NotImplementedError("takeout() is not supported in serverless testing mode")
