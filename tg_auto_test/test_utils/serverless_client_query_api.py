from typing import Union

from telethon.tl.types import User

from tg_auto_test.test_utils.models import ServerlessMessage


class ServerlessClientQueryAPI:
    """Mixin providing query API methods for ServerlessTelegramClient.

    This class contains query methods like get_me, get_dialogs, and get_messages
    that form the data retrieval interface for the Telegram client in tests.
    These methods are extracted from ServerlessClientPublicAPI to provide
    headroom for additional client methods.
    """

    async def get_me(self, input_peer: bool = False) -> User:
        if input_peer is True:
            raise NotImplementedError("input_peer=True not supported")
        return User(id=self._user_id, is_self=True, first_name=self._first_name, bot=False, access_hash=0)

    async def get_dialogs(
        self,
        limit: int | None = None,
        *,
        offset_date: object = None,
        offset_id: int = 0,
        offset_peer: object = None,
        ignore_pinned: bool = False,
        ignore_migrated: bool = False,
        folder: int | None = None,
        archived: bool = False,
    ) -> list[object]:
        del limit, offset_date, offset_id, offset_peer, ignore_pinned, ignore_migrated, folder, archived
        return []

    async def get_messages(
        self,
        entity: object,
        limit: int | None = None,
        *,
        offset_date: object = None,
        offset_id: int = 0,
        max_id: int = 0,
        min_id: int = 0,
        add_offset: int = 0,
        search: str | None = None,
        filter: object = None,
        from_user: object = None,
        wait_time: float | None = None,
        ids: int | list[int] | None = None,
        reverse: bool = False,
        reply_to: int | None = None,
        scheduled: bool = False,
    ) -> Union[ServerlessMessage, list[ServerlessMessage], None]:
        del entity
        if ids is None and limit is None:
            raise ValueError("Either 'ids' or 'limit' must be provided")
        if [
            limit,
            offset_date,
            offset_id,
            max_id,
            min_id,
            add_offset,
            search,
            filter,
            from_user,
            wait_time,
            reverse,
            reply_to,
            scheduled,
        ] != [None, None, 0, 0, 0, 0, None, None, None, None, False, None, False]:
            raise NotImplementedError("Parameter not supported")
        return (
            ServerlessMessage(id=ids, _click_callback=self._handle_click)
            if isinstance(ids, int)
            else (
                [ServerlessMessage(id=msg_id, _click_callback=self._handle_click) for msg_id in ids]
                if ids is not None
                else None
            )
        )
