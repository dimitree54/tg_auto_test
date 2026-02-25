from tg_auto_test.test_utils.models import ServerlessMessage
from tg_auto_test.test_utils.serverless_client_auth_stubs import ServerlessClientAuthStubs
from tg_auto_test.test_utils.serverless_telegram_conversation import ServerlessTelegramConversation


class ServerlessClientPublicAPI(ServerlessClientAuthStubs):
    """Mixin providing public API methods for ServerlessTelegramClient.

    This class contains the client methods that form the public interface
    for interacting with the Telegram client in tests. These methods are
    extracted from ServerlessTelegramClientCore to free up space for
    additional methods.
    """

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
        if parse_mode != () or not link_preview or force_document or clear_draft or supports_streaming:
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
