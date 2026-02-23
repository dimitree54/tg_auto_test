"""DemoServer class and FastAPI app factory for backend-agnostic Telegram demo UI."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any  # noqa: TID251

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from tg_auto_test.demo_ui.server.backends.duck_backend import DuckBackend
from tg_auto_test.demo_ui.server.backends.telethon_backend import TelethonBackend
from tg_auto_test.demo_ui.server.file_store import FileStore
from tg_auto_test.demo_ui.server.routes import register_routes


class DemoServer:
    """Backend-agnostic demo server for Telegram bot testing UI."""

    def __init__(
        self,
        client: Any,  # noqa: ANN401
        peer: str,
        *,
        timeout: float = 10.0,
        manage_client_lifecycle: bool = True,
        backend_type: str = "auto",
    ) -> None:
        """Initialize demo server with configurable backend.

        Args:
            client: Telegram client (Telethon or serverless)
            peer: Peer identifier (bot username, etc.)
            timeout: Conversation timeout in seconds
            manage_client_lifecycle: Whether to connect/disconnect client
            backend_type: "telethon", "duck", or "auto" for auto-detection
        """
        if not peer:
            raise ValueError("Peer must be specified (no hardcoded peer allowed)")

        self.peer = peer
        self.timeout = timeout
        self.file_store = FileStore()

        # Determine backend type
        if backend_type == "auto":
            backend_type = self._detect_backend_type(client)

        # Create backend
        if backend_type == "telethon":
            self.backend = TelethonBackend(client, manage_client_lifecycle)
        elif backend_type == "duck":
            self.backend = DuckBackend(client, manage_client_lifecycle)
        else:
            raise ValueError(f"Unknown backend type: {backend_type}")

    def _detect_backend_type(self, client: Any) -> str:  # noqa: ANN401
        """Auto-detect backend type based on client capabilities."""
        # Check for serverless client methods
        if hasattr(client, "process_callback_query") or hasattr(client, "conversation"):
            return "duck"
        # Check for Telethon client methods
        if hasattr(client, "get_messages") or hasattr(client, "get_dialogs"):
            return "telethon"
        # Default to duck for unknown clients
        return "duck"

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG002
        """FastAPI lifespan context manager."""
        await self.backend.connect()
        yield
        await self.backend.disconnect()

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
    manage_client_lifecycle: bool = True,
    backend_type: str = "auto",
    static_dir: Path | None = None,
    templates_dir: Path | None = None,
) -> FastAPI:
    """Factory function to create a demo FastAPI app."""
    server = DemoServer(
        client=client,
        peer=peer,
        timeout=timeout,
        manage_client_lifecycle=manage_client_lifecycle,
        backend_type=backend_type,
    )
    return server.create_app(static_dir=static_dir, templates_dir=templates_dir)
