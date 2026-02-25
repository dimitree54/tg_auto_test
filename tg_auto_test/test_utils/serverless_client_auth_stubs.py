"""Auth and connection-related stubs for ServerlessTelegramClient.

This module provides NotImplementedError-raising stubs for Telethon auth and connection
methods that are not supported in serverless testing mode.
"""

from tg_auto_test.test_utils.serverless_client_admin_stubs import ServerlessClientAdminStubs


class ServerlessClientAuthStubs(ServerlessClientAdminStubs):
    """Mixin providing auth/connection stubs for ServerlessTelegramClient."""

    async def start(self, *args, **kwargs) -> None:
        """Start the client (auth flow). Not supported in serverless testing mode."""
        raise NotImplementedError("start() is not supported in serverless testing mode")

    async def sign_in(self, *args, **kwargs) -> object:
        """Sign in with phone/password. Not supported in serverless testing mode."""
        raise NotImplementedError("sign_in() is not supported in serverless testing mode")

    async def sign_up(self, *args, **kwargs) -> object:
        """Sign up new account. Not supported in serverless testing mode."""
        raise NotImplementedError("sign_up() is not supported in serverless testing mode")

    async def send_code_request(self, *args, **kwargs) -> object:
        """Request auth code. Not supported in serverless testing mode."""
        raise NotImplementedError("send_code_request() is not supported in serverless testing mode")

    async def log_out(self, *args, **kwargs) -> bool:
        """Log out from the client. Not supported in serverless testing mode."""
        raise NotImplementedError("log_out() is not supported in serverless testing mode")

    async def qr_login(self, *args, **kwargs) -> object:
        """QR code login. Not supported in serverless testing mode."""
        raise NotImplementedError("qr_login() is not supported in serverless testing mode")

    async def edit_2fa(self, *args, **kwargs) -> bool:
        """Edit 2FA settings. Not supported in serverless testing mode."""
        raise NotImplementedError("edit_2fa() is not supported in serverless testing mode")

    @property
    def disconnected(self) -> bool:
        """Connection state property. Not supported in serverless testing mode."""
        raise NotImplementedError("disconnected is not supported in serverless testing mode")

    def set_proxy(self, *args, **kwargs) -> None:
        """Set proxy configuration. Not supported in serverless testing mode."""
        raise NotImplementedError("set_proxy() is not supported in serverless testing mode")

    def set_receive_updates(self, *args, **kwargs) -> None:
        """Configure update reception. Not supported in serverless testing mode."""
        raise NotImplementedError("set_receive_updates() is not supported in serverless testing mode")

    def run_until_disconnected(self, *args, **kwargs) -> None:
        """Run client until disconnected. Not supported in serverless testing mode."""
        raise NotImplementedError("run_until_disconnected() is not supported in serverless testing mode")
