"""Backend for serverless/duck-typed clients (tg-auto-test compatible)."""

from telegram import BotCommandScopeChat

from tg_auto_test.demo_ui.server.backends.base import BaseConversationContext, ConversationContext, TelegramBackend
from tg_auto_test.test_utils.models import ServerlessMessage
from tg_auto_test.test_utils.serverless_telegram_conversation import ServerlessTelegramConversation


class DuckConversationContext(BaseConversationContext):
    """Wrapper for serverless conversation context."""

    def __init__(self, conversation: ServerlessTelegramConversation) -> None:
        super().__init__(conversation)

    async def get_response(self) -> ServerlessMessage:
        return await self._conv.get_response()


class DuckBackend(TelegramBackend):
    """Backend for serverless/duck-typed Telegram clients."""

    def conversation(self, peer: str, timeout: float) -> ConversationContext:
        """Create a conversation context using the serverless client."""
        del timeout  # serverless client doesn't use timeout in conversation()
        conv = self.client.conversation(peer)  # type: ignore[attr-defined]
        return DuckConversationContext(conv)

    async def get_bot_state(self) -> tuple[list[dict[str, str]], str]:
        """Get bot commands and menu button type from PTB application."""
        try:
            scope = BotCommandScopeChat(chat_id=self.client.chat_id)  # type: ignore[attr-defined]
            commands = await self.client.application.bot.get_my_commands(scope=scope)  # type: ignore[attr-defined]
            menu_btn = await self.client.application.bot.get_chat_menu_button(chat_id=self.client.chat_id)  # type: ignore[attr-defined]
            menu_btn_type = str(getattr(menu_btn, "type", "default"))

            command_list = [{"command": cmd.command, "description": cmd.description} for cmd in commands]
            return command_list, menu_btn_type
        except (AttributeError, ImportError):
            # Fallback if PTB integration not available
            return [], "default"

    async def handle_callback(self, peer: str, message_id: int, callback_data: str) -> ServerlessMessage:
        """Handle inline button callback via process_callback_query."""
        del peer  # not used in serverless mode
        return await self.client.process_callback_query(message_id, callback_data)  # type: ignore[attr-defined]

    async def handle_invoice_payment(self, message_id: int) -> ServerlessMessage:
        """Handle Stars payment via simulate_stars_payment."""
        await self.client.simulate_stars_payment(message_id)  # type: ignore[attr-defined]
        return self.client.pop_response()  # type: ignore[attr-defined]

    async def connect(self) -> None:
        """Connect the serverless client."""
        if self.manage_lifecycle and hasattr(self.client, "connect"):
            await self.client.connect()  # type: ignore[attr-defined]

    async def disconnect(self) -> None:
        """Disconnect the serverless client."""
        if self.manage_lifecycle and hasattr(self.client, "disconnect"):
            await self.client.disconnect()  # type: ignore[attr-defined]

    def supports_capability(self, capability: str) -> bool:
        """Check serverless client capabilities."""
        if capability == "callback_queries":
            return hasattr(self.client, "process_callback_query")
        if capability == "invoice_payments":
            return hasattr(self.client, "simulate_stars_payment")
        if capability == "bot_state":
            return hasattr(self.client, "application")
        return False
