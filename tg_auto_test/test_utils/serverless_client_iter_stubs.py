"""Iteration and download-related stubs for ServerlessTelegramClient.

This module provides NotImplementedError-raising stubs for Telethon iteration and download
methods that are not supported in serverless testing mode.
"""

from tg_auto_test.test_utils.serverless_client_misc_stubs import ServerlessClientMiscStubs


class ServerlessClientIterStubs(ServerlessClientMiscStubs):
    """Mixin providing iteration/download stubs for ServerlessTelegramClient."""

    async def iter_dialogs(self, *args, **kwargs) -> object:
        """Iterate dialogs/conversations. Not supported in serverless testing mode."""
        raise NotImplementedError("iter_dialogs() is not supported in serverless testing mode")

    async def iter_messages(self, *args, **kwargs) -> object:
        """Iterate messages in chat. Not supported in serverless testing mode."""
        raise NotImplementedError("iter_messages() is not supported in serverless testing mode")

    async def iter_drafts(self, *args, **kwargs) -> object:
        """Iterate draft messages. Not supported in serverless testing mode."""
        raise NotImplementedError("iter_drafts() is not supported in serverless testing mode")

    async def iter_profile_photos(self, *args, **kwargs) -> object:
        """Iterate profile photos. Not supported in serverless testing mode."""
        raise NotImplementedError("iter_profile_photos() is not supported in serverless testing mode")

    async def iter_download(self, *args, **kwargs) -> object:
        """Iterate file download chunks. Not supported in serverless testing mode."""
        raise NotImplementedError("iter_download() is not supported in serverless testing mode")

    async def download_file(self, *args, **kwargs) -> bytes:
        """Download file by file reference. Not supported in serverless testing mode."""
        raise NotImplementedError("download_file() is not supported in serverless testing mode")

    async def download_profile_photo(self, *args, **kwargs) -> str | None:
        """Download profile photo. Not supported in serverless testing mode."""
        raise NotImplementedError("download_profile_photo() is not supported in serverless testing mode")

    async def upload_file(self, *args, **kwargs) -> object:
        """Upload file to Telegram servers. Not supported in serverless testing mode."""
        raise NotImplementedError("upload_file() is not supported in serverless testing mode")

    async def get_profile_photos(self, *args, **kwargs) -> object:
        """Get profile photos list. Not supported in serverless testing mode."""
        raise NotImplementedError("get_profile_photos() is not supported in serverless testing mode")

    async def get_drafts(self, *args, **kwargs) -> object:
        """Get draft messages. Not supported in serverless testing mode."""
        raise NotImplementedError("get_drafts() is not supported in serverless testing mode")
