"""Backend for real Telethon clients."""

import io
from typing import Any  # noqa: TID251

from tg_auto_test.demo_ui.server.backends.base import BaseConversationContext, ConversationContext, TelegramBackend
from tg_auto_test.test_utils.models import ServerlessMessage


class TelethonConversationContext(BaseConversationContext):
    """Wrapper for Telethon conversation context."""

    def __init__(self, telethon_conv: Any) -> None:  # noqa: ANN401
        super().__init__(telethon_conv)

    def _preprocess_file(self, file: Any) -> Any:  # noqa: ANN401
        """Preprocess file for Telethon - convert bytes to BytesIO."""
        if isinstance(file, bytes):
            # Convert bytes to BytesIO for Telethon
            file_obj = io.BytesIO(file)
            file_obj.name = "upload"  # Default name
            return file_obj
        return file

    def _build_send_file_kwargs(
        self,
        *,
        caption: str = "",
        force_document: bool = False,
        voice_note: bool = False,
        video_note: bool = False,
    ) -> dict[str, Any]:
        """Build kwargs dict for Telethon send_file."""
        kwargs = {}
        if caption:
            kwargs["caption"] = caption
        if force_document:
            kwargs["force_document"] = True
        if voice_note:
            kwargs["voice_note"] = True
        if video_note:
            kwargs["video_note"] = True
        return kwargs

    async def get_response(self) -> ServerlessMessage:
        """Get response from Telethon and convert to ServerlessMessage."""
        telethon_msg = await self._conv.get_response()
        # Convert Telethon message to ServerlessMessage
        # This is a minimal conversion - in practice you'd want more complete mapping
        return ServerlessMessage(
            id=telethon_msg.id,
            text=telethon_msg.text or "",
            # TODO: Add media conversion when needed
        )


class TelethonBackend(TelegramBackend):
    """Backend for real Telethon clients."""

    def conversation(self, peer: str, timeout: float) -> ConversationContext:
        """Create a conversation context using Telethon client."""
        conv = self.client.conversation(peer, timeout=timeout)
        return TelethonConversationContext(conv)

    async def get_bot_state(self) -> tuple[list[dict[str, str]], str]:
        """Get bot state - limited support for Telethon."""
        # Telethon doesn't provide easy access to bot commands/menu like PTB
        # Return empty state as best-effort fallback
        return [], "default"

    async def handle_callback(self, peer: str, message_id: int, callback_data: str) -> ServerlessMessage:
        """Handle inline button callback via Telethon."""
        # Get the message and click the button
        msg = await self.client.get_messages(peer, ids=message_id)
        if not msg:
            raise RuntimeError(f"Message {message_id} not found")

        # Click the button
        await msg.click(data=callback_data.encode())

        # TODO: Implement proper response fetching
        # This is a simplified version - real implementation would need
        # to determine how to get the bot's response after clicking
        return ServerlessMessage(id=0, text="Callback processed")

    async def handle_invoice_payment(self, message_id: int) -> ServerlessMessage:
        """Handle invoice payment - not supported in Telethon backend."""
        del message_id  # unused
        raise RuntimeError("Invoice payments not supported in Telethon backend")

    async def connect(self) -> None:
        """Connect the Telethon client."""
        if self.manage_lifecycle and hasattr(self.client, "connect"):
            await self.client.connect()

    async def disconnect(self) -> None:
        """Disconnect the Telethon client."""
        if self.manage_lifecycle and hasattr(self.client, "disconnect"):
            await self.client.disconnect()

    def supports_capability(self, capability: str) -> bool:
        """Check Telethon client capabilities."""
        if capability == "callback_queries":
            return True  # Telethon supports clicking buttons
        if capability == "invoice_payments":
            return False  # Not implemented for v0.1
        if capability == "bot_state":
            return False  # Limited support
        return False
