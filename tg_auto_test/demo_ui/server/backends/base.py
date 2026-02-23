"""Backend protocol/ABC for different Telegram client implementations."""

from abc import ABC, abstractmethod
from typing import Any, Protocol  # noqa: TID251

from tg_auto_test.test_utils.models import ServerlessMessage


class BaseConversationContext:
    """Base class with common conversation context functionality."""

    def __init__(self, conversation: Any) -> None:  # noqa: ANN401
        self._conv = conversation

    async def __aenter__(self) -> "ConversationContext":
        await self._conv.__aenter__()
        return self  # type: ignore[return-value]

    async def __aexit__(self, *args: object) -> None:
        await self._conv.__aexit__(*args)

    async def send_message(self, text: str) -> None:
        await self._conv.send_message(text)

    async def send_file(
        self,
        file: Any,  # noqa: ANN401
        *,
        caption: str = "",
        force_document: bool = False,
        voice_note: bool = False,
        video_note: bool = False,
    ) -> None:
        """Send file with common parameter handling."""
        processed_file = self._preprocess_file(file)
        kwargs = self._build_send_file_kwargs(
            caption=caption,
            force_document=force_document,
            voice_note=voice_note,
            video_note=video_note,
        )
        await self._send_file_impl(processed_file, **kwargs)

    def _preprocess_file(self, file: Any) -> Any:  # noqa: ANN401
        """Preprocess file before sending. Override in subclasses if needed."""
        return file

    def _build_send_file_kwargs(
        self,
        *,
        caption: str = "",
        force_document: bool = False,
        voice_note: bool = False,
        video_note: bool = False,
    ) -> dict[str, Any]:
        """Build kwargs dict for send_file. Override in subclasses if needed."""
        kwargs = {}
        if caption:
            kwargs["caption"] = caption
        if force_document:
            kwargs["force_document"] = force_document
        if voice_note:
            kwargs["voice_note"] = voice_note
        if video_note:
            kwargs["video_note"] = video_note
        return kwargs

    async def _send_file_impl(self, file: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """Actual file sending implementation. Override in subclasses if needed."""
        await self._conv.send_file(file, **kwargs)


class ConversationContext(Protocol):
    """Protocol for conversation context managers."""

    async def __aenter__(self) -> "ConversationContext": ...

    async def __aexit__(self, *args: object) -> None: ...

    async def send_message(self, text: str) -> None: ...

    async def send_file(
        self,
        file: Any,  # noqa: ANN401
        *,
        caption: str = "",
        force_document: bool = False,
        voice_note: bool = False,
        video_note: bool = False,
    ) -> None: ...

    async def get_response(self) -> ServerlessMessage: ...


class TelegramBackend(ABC):
    """Abstract base class for Telegram client backends."""

    def __init__(self, client: Any, manage_lifecycle: bool = True) -> None:  # noqa: ANN401
        self.client = client
        self.manage_lifecycle = manage_lifecycle

    @abstractmethod
    def conversation(self, peer: str, timeout: float) -> ConversationContext:
        """Create a conversation context manager."""

    @abstractmethod
    async def get_bot_state(self) -> tuple[list[dict[str, str]], str]:
        """Get bot commands and menu button type.

        Returns: (commands list, menu_button_type)
        """

    @abstractmethod
    async def handle_callback(self, peer: str, message_id: int, callback_data: str) -> ServerlessMessage:
        """Handle inline button callback."""

    @abstractmethod
    async def handle_invoice_payment(self, message_id: int) -> ServerlessMessage:
        """Handle invoice payment (Stars payment)."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect the client if lifecycle is managed."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect the client if lifecycle is managed."""

    @abstractmethod
    def supports_capability(self, capability: str) -> bool:
        """Check if backend supports a specific capability.

        Capabilities:
        - "callback_queries": inline button callbacks
        - "invoice_payments": Stars payment simulation
        - "bot_state": get bot commands/menu
        """
