from typing import Union

from telethon.tl.types import User

from tg_auto_test.test_utils.models import ServerlessMessage
from tg_auto_test.test_utils.serverless_telegram_conversation import ServerlessTelegramConversation


class ServerlessClientPublicAPI:
    """Mixin providing public API methods for ServerlessTelegramClient.

    This class contains the client methods that form the public interface
    for interacting with the Telegram client in tests. These methods are
    extracted from ServerlessTelegramClientCore to free up space for
    additional methods.
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

    def conversation(
        self,
        entity: object,
        *,
        timeout: float = 60.0,
        total_timeout: float | None = None,
        max_messages: int = 100,
        exclusive: bool = True,
        replies_are_responses: bool = True,
    ) -> ServerlessTelegramConversation:
        del entity, timeout
        if [total_timeout, max_messages, exclusive, replies_are_responses] != [None, 100, True, True]:
            raise NotImplementedError("Parameter not supported")
        return ServerlessTelegramConversation(client=self)

    async def send_message(
        self,
        entity: object,
        message: str = "",
        *,
        reply_to: object = None,
        attributes: object = None,
        parse_mode: object = (),
        formatting_entities: object = None,
        link_preview: bool = True,
        file: object = None,
        thumb: object = None,
        force_document: bool = False,
        clear_draft: bool = False,
        buttons: object = None,
        silent: object = None,
        background: object = None,
        supports_streaming: bool = False,
        schedule: object = None,
        comment_to: object = None,
        nosound_video: object = None,
        send_as: object = None,
        message_effect_id: object = None,
    ) -> ServerlessMessage:
        """Send a text message to an entity. Only supports sending to the bot chat."""
        if entity != self._chat_id:
            raise NotImplementedError("send_message to entities other than the bot chat is not supported")

        # Check for non-default parameters and raise NotImplementedError
        non_default_params = [
            reply_to,
            attributes,
            formatting_entities,
            file,
            thumb,
            buttons,
            silent,
            background,
            schedule,
            comment_to,
            nosound_video,
            send_as,
            message_effect_id,
        ]
        if any(param is not None for param in non_default_params):
            raise NotImplementedError("Non-default parameters are not supported")

        # Check for non-default boolean parameters
        if parse_mode != () or not link_preview or force_document or clear_draft or not supports_streaming:
            raise NotImplementedError("Non-default parameters are not supported")

        return await self._process_text_message(message)

    async def download_media(
        self,
        message: object,
        file: object = None,
        *,
        thumb: object = None,
        progress_callback: object = None,
    ) -> bytes | None:
        """Download media from a message. Delegates to the message's download_media method."""
        if not hasattr(message, "download_media"):
            raise NotImplementedError("Message does not support media download")
        return await message.download_media(file=file, thumb=thumb, progress_callback=progress_callback)  # type: ignore[attr-defined]
