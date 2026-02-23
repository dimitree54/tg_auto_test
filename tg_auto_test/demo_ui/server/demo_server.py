"""DemoServer class and FastAPI app factory for Telethon-targeted Telegram demo UI."""

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any  # noqa: TID251

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from tg_auto_test.demo_ui.server.file_store import FileStore
from tg_auto_test.demo_ui.server.routes import register_routes

# Expose asset paths for consumers
STATIC_DIR = Path(__file__).parent / "static"
TEMPLATES_DIR = Path(__file__).parent / "templates"


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

    def create_app(self, static_dir: Path | None = None, templates_dir: Path | None = None) -> FastAPI:
        """Create and configure FastAPI application."""
        app = FastAPI(lifespan=self.lifespan)

        # Store server instance in app state for endpoint access
        app.state.demo_server = self

        # Mount static files if directory provided
        if static_dir and static_dir.exists():
            app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

        # Register routes
        register_routes(app, self, templates_dir)

        return app


def create_demo_app(
    client: Any,  # noqa: ANN401
    peer: str,
    *,
    timeout: float = 10.0,
    static_dir: Path | None = None,
    templates_dir: Path | None = None,
    on_reset: Callable[[Any], Any] | None = None,  # noqa: ANN401
) -> FastAPI:
    """Factory function to create a demo FastAPI app."""
    server = DemoServer(
        client=client,
        peer=peer,
        timeout=timeout,
        on_reset=on_reset,
    )
    return server.create_app(static_dir=static_dir, templates_dir=templates_dir)
