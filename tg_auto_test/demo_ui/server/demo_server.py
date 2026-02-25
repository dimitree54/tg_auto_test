"""DemoServer class and FastAPI app factory for Telethon-targeted Telegram demo UI."""

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Protocol

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from tg_auto_test.demo_ui.server.file_store import FileStore
from tg_auto_test.demo_ui.server.routes import register_routes

# Internal asset paths
_STATIC_DIR = Path(__file__).parent / "static"
_TEMPLATES_DIR = Path(__file__).parent / "templates"


class DemoConversationProtocol(Protocol):
    """Protocol for conversation context manager returned by client.conversation()."""

    async def send_message(self, text: str) -> object:
        """Send a text message."""
        ...

    async def get_response(self, message: object = None, *, timeout: float | None = None) -> object:
        """Get the bot's response to the last sent message."""
        ...

    async def send_file(
        self,
        file: object,
        *,
        caption: str = "",
        force_document: bool = False,
        voice_note: bool = False,
        video_note: bool = False,
    ) -> object:
        """Send a file message."""
        ...

    async def __aenter__(self) -> "DemoConversationProtocol":
        """Enter the async context manager."""
        ...

    async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> object:  # noqa: ARG002
        """Exit the async context manager."""
        ...


class DemoClientProtocol(Protocol):
    """Protocol for the DemoServer client parameter."""

    async def connect(self) -> None:
        """Connect the client."""
        ...

    async def disconnect(self) -> None:
        """Disconnect the client."""
        ...

    def conversation(self, entity: object, *, timeout: float = 60.0) -> DemoConversationProtocol:
        """Create a conversation context manager."""
        ...

    async def get_messages(
        self, entity: object, limit: int | None = None, *, ids: int | list[int] | None = None
    ) -> object:
        """Get messages by ID for Telethon compatibility."""
        ...

    async def __call__(self, request: object) -> object:
        """Execute Telethon TL request."""
        ...


class DemoServer:
    """Telethon-targeted demo server for Telegram bot testing UI."""

    def __init__(
        self,
        client: DemoClientProtocol,
        peer: str,
        *,
        timeout: float = 10.0,
        on_action: Callable[[str, DemoClientProtocol], Awaitable[None]] | None = None,
    ) -> None:
        """Initialize demo server with Telethon client.

        Args:
            client: Telegram client implementing Telethon interface
            peer: Peer identifier (bot username, etc.)
            timeout: Conversation timeout in seconds
            on_action: Optional async callback called after every demo server action completes
        """
        if not peer:
            raise ValueError("Peer must be specified (no hardcoded peer allowed)")

        self.client = client
        self.peer = peer
        self.timeout = timeout
        self.on_action = on_action
        self.file_store = FileStore()

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG002
        """FastAPI lifespan context manager."""
        await self.client.connect()
        yield
        await self.client.disconnect()

    def create_app(self) -> FastAPI:
        """Create and configure FastAPI application."""
        app = FastAPI(lifespan=self.lifespan)

        # Store server instance in app state for endpoint access
        app.state.demo_server = self

        # Mount static files using library's own assets
        app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

        # Register routes using library's own templates
        register_routes(app, self, _TEMPLATES_DIR)

        return app


def create_demo_app(
    client: DemoClientProtocol,
    peer: str,
    *,
    timeout: float = 10.0,
    on_action: Callable[[str, DemoClientProtocol], Awaitable[None]] | None = None,
) -> FastAPI:
    """Factory function to create a demo FastAPI app."""
    server = DemoServer(
        client=client,
        peer=peer,
        timeout=timeout,
        on_action=on_action,
    )
    return server.create_app()
