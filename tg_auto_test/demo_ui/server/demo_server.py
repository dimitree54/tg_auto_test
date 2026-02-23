"""DemoServer class and FastAPI app factory for Telethon-targeted Telegram demo UI."""

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any  # noqa: TID251

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from tg_auto_test.demo_ui.server.file_store import FileStore
from tg_auto_test.demo_ui.server.routes import register_routes

# Internal asset paths
_STATIC_DIR = Path(__file__).parent / "static"
_TEMPLATES_DIR = Path(__file__).parent / "templates"


class DemoServer:
    """Telethon-targeted demo server for Telegram bot testing UI."""

    def __init__(
        self,
        client: Any,  # noqa: ANN401
        peer: str,
        *,
        timeout: float = 10.0,
        on_reset: Callable[[Any], Any] | None = None,  # noqa: ANN401
    ) -> None:
        """Initialize demo server with Telethon client.

        Args:
            client: Telegram client implementing Telethon interface
            peer: Peer identifier (bot username, etc.)
            timeout: Conversation timeout in seconds
            on_reset: Optional async callback called during reset after built-in cleanup
        """
        if not peer:
            raise ValueError("Peer must be specified (no hardcoded peer allowed)")

        self.client = client
        self.peer = peer
        self.timeout = timeout
        self.on_reset = on_reset
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
        if _STATIC_DIR.exists():
            app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

        # Register routes using library's own templates
        register_routes(app, self, _TEMPLATES_DIR)

        return app


def create_demo_app(
    client: Any,  # noqa: ANN401
    peer: str,
    *,
    timeout: float = 10.0,
    on_reset: Callable[[Any], Any] | None = None,  # noqa: ANN401
) -> FastAPI:
    """Factory function to create a demo FastAPI app."""
    server = DemoServer(
        client=client,
        peer=peer,
        timeout=timeout,
        on_reset=on_reset,
    )
    return server.create_app()
