from telethon.tl.types import InputPeerUser

from tg_auto_test.test_utils.models import TelegramApiCall
from tg_auto_test.test_utils.ptb_types import BuildApplication
from tg_auto_test.test_utils.serverless_telegram_client_core import ServerlessTelegramClientCore
from tg_auto_test.test_utils.serverless_telethon_rpc import (
    TelethonRequest,
    TelethonResponse,
    handle_telethon_request,
)

# Export the TelegramApiCall class for consumers
__all__ = ["ServerlessTelegramClient", "TelegramApiCall"]


class ServerlessTelegramClient(ServerlessTelegramClientCore):
    def __init__(
        self,
        build_application: BuildApplication,
        user_id: int = 9001,
        first_name: str = "Alice",
        *,
        bot_username: str = "test_bot",
        bot_first_name: str = "TestBot",
    ) -> None:
        super().__init__(
            build_application=build_application,
            user_id=user_id,
            first_name=first_name,
            bot_username=bot_username,
            bot_first_name=bot_first_name,
        )

    async def get_input_entity(self, peer: object) -> InputPeerUser:
        del peer
        return InputPeerUser(user_id=999_999, access_hash=0)

    async def __call__(self, request: TelethonRequest) -> TelethonResponse:
        return await handle_telethon_request(self, request)
