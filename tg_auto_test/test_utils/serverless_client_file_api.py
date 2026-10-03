from tg_auto_test.test_utils.models import ServerlessMessage
from tg_auto_test.test_utils.serverless_client_public_api import ServerlessClientPublicAPI


class ServerlessClientFileAPI(ServerlessClientPublicAPI):
    async def send_file(
        self,
        entity: object,
        file: object,
        *,
        caption: object = None,
        force_document: bool = False,
        mime_type: object = None,
        file_size: object = None,
        clear_draft: bool = False,
        progress_callback: object = None,
        reply_to: object = None,
        attributes: object = None,
        thumb: object = None,
        allow_cache: bool = True,
        parse_mode: object = (),
        formatting_entities: object = None,
        voice_note: bool = False,
        video_note: bool = False,
        buttons: object = None,
        silent: object = None,
        background: object = None,
        supports_streaming: bool = False,
        schedule: object = None,
        comment_to: object = None,
        ttl: object = None,
        nosound_video: object = None,
        send_as: object = None,
        message_effect_id: object = None,
        **kwargs: object,
    ) -> ServerlessMessage:
        """Send a file to an entity. Only supports sending to the bot chat."""
        if entity != self._chat_id:
            raise NotImplementedError("send_file to entities other than the bot chat is not supported")

        # Check for extra kwargs
        if kwargs:
            raise NotImplementedError("Extra keyword arguments are not supported")

        # Check for non-default parameters (excluding caption, force_document, voice_note, video_note)
        non_default_params = [
            mime_type,
            file_size,
            progress_callback,
            reply_to,
            attributes,
            thumb,
            buttons,
            silent,
            background,
            schedule,
            comment_to,
            ttl,
            nosound_video,
            send_as,
            message_effect_id,
        ]
        if any(param is not None for param in non_default_params):
            raise NotImplementedError("Non-default parameters are not supported")

        # Check for non-default boolean parameters (excluding the ones we support)
        if clear_draft or not allow_cache or supports_streaming:
            raise NotImplementedError("Non-default parameters are not supported")

        return await self._process_file_message(
            file,  # type: ignore[arg-type]
            caption=str(caption or ""),
            parse_mode=parse_mode,
            formatting_entities=formatting_entities,
            force_document=force_document,
            voice_note=voice_note,
            video_note=video_note,
        )
