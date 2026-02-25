"""Admin and moderation-related stubs for ServerlessTelegramClient.

This module provides NotImplementedError-raising stubs for Telethon admin and moderation
methods that are not supported in serverless testing mode.
"""

from tg_auto_test.test_utils.serverless_client_iter_stubs import ServerlessClientIterStubs


class ServerlessClientAdminStubs(ServerlessClientIterStubs):
    """Mixin providing admin/moderation stubs for ServerlessTelegramClient."""

    async def edit_admin(self, *args, **kwargs) -> object:
        """Edit admin permissions. Not supported in serverless testing mode."""
        raise NotImplementedError("edit_admin() is not supported in serverless testing mode")

    async def edit_permissions(self, *args, **kwargs) -> object:
        """Edit user permissions. Not supported in serverless testing mode."""
        raise NotImplementedError("edit_permissions() is not supported in serverless testing mode")

    async def kick_participant(self, *args, **kwargs) -> object:
        """Kick participant from chat. Not supported in serverless testing mode."""
        raise NotImplementedError("kick_participant() is not supported in serverless testing mode")

    async def get_permissions(self, *args, **kwargs) -> object:
        """Get user permissions. Not supported in serverless testing mode."""
        raise NotImplementedError("get_permissions() is not supported in serverless testing mode")

    async def get_admin_log(self, *args, **kwargs) -> object:
        """Get admin log. Not supported in serverless testing mode."""
        raise NotImplementedError("get_admin_log() is not supported in serverless testing mode")

    async def iter_admin_log(self, *args, **kwargs) -> object:
        """Iterate admin log entries. Not supported in serverless testing mode."""
        raise NotImplementedError("iter_admin_log() is not supported in serverless testing mode")

    async def get_participants(self, *args, **kwargs) -> object:
        """Get chat participants. Not supported in serverless testing mode."""
        raise NotImplementedError("get_participants() is not supported in serverless testing mode")

    async def iter_participants(self, *args, **kwargs) -> object:
        """Iterate chat participants. Not supported in serverless testing mode."""
        raise NotImplementedError("iter_participants() is not supported in serverless testing mode")

    async def get_stats(self, *args, **kwargs) -> object:
        """Get chat statistics. Not supported in serverless testing mode."""
        raise NotImplementedError("get_stats() is not supported in serverless testing mode")

    async def pin_message(self, *args, **kwargs) -> object:
        """Pin message in chat. Not supported in serverless testing mode."""
        raise NotImplementedError("pin_message() is not supported in serverless testing mode")

    async def unpin_message(self, *args, **kwargs) -> object:
        """Unpin message in chat. Not supported in serverless testing mode."""
        raise NotImplementedError("unpin_message() is not supported in serverless testing mode")

    async def edit_message(self, *args, **kwargs) -> object:
        """Edit existing message. Not supported in serverless testing mode."""
        raise NotImplementedError("edit_message() is not supported in serverless testing mode")

    async def delete_messages(self, *args, **kwargs) -> object:
        """Delete messages from chat. Not supported in serverless testing mode."""
        raise NotImplementedError("delete_messages() is not supported in serverless testing mode")

    async def forward_messages(self, *args, **kwargs) -> object:
        """Forward messages to another chat. Not supported in serverless testing mode."""
        raise NotImplementedError("forward_messages() is not supported in serverless testing mode")

    async def send_read_acknowledge(self, *args, **kwargs) -> bool:
        """Mark messages as read. Not supported in serverless testing mode."""
        raise NotImplementedError("send_read_acknowledge() is not supported in serverless testing mode")
