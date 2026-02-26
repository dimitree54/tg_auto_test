"""PuppetRecorderServer: experimental demo server with session recording capabilities."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse

from tg_auto_test.demo_ui.puppet_recorder.recorder_models import RecordingSession
from tg_auto_test.demo_ui.puppet_recorder.recorder_routes import register_recorder_routes
from tg_auto_test.demo_ui.server.demo_server import DemoClientProtocol
from tg_auto_test.demo_ui.server.file_store import FileStore

_TEMPLATES_DIR = Path(__file__).parent / "templates"


class PuppetRecorderServer:
    """Experimental demo server that records user-bot interactions for test generation."""

    def __init__(
        self,
        client: DemoClientProtocol,
        peer: str,
        *,
        timeout: float = 10.0,
    ) -> None:
        if not peer:
            raise ValueError("Peer must be specified")

        self.client = client
        self.peer = peer
        self.timeout = timeout
        self.file_store = FileStore()
        self.session = RecordingSession()

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG002
        """FastAPI lifespan: connect client on startup, disconnect on shutdown."""
        await self.client.connect()
        yield
        await self.client.disconnect()

    def create_app(self) -> FastAPI:
        """Create and configure the FastAPI application with recording routes."""
        app = FastAPI(lifespan=self.lifespan)
        app.state.recorder_server = self

        @app.get("/", response_model=None)
        async def index() -> HTMLResponse | FileResponse:
            template_path = _TEMPLATES_DIR / "puppet_recorder.html"
            if template_path.exists():
                return FileResponse(template_path)
            return HTMLResponse("<h1>Puppet Recorder</h1><p>Template not found.</p>", status_code=404)

        register_recorder_routes(app, self)
        return app


def create_puppet_recorder_app(
    client: DemoClientProtocol,
    peer: str,
    *,
    timeout: float = 10.0,
) -> FastAPI:
    """Factory function to create a puppet recorder FastAPI app."""
    server = PuppetRecorderServer(client=client, peer=peer, timeout=timeout)
    return server.create_app()
