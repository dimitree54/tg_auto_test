"""Tests for the puppet recorder server initialization and recording control routes."""

from typing import cast
from unittest.mock import MagicMock  # noqa: TID251

from fastapi.testclient import TestClient
import pytest

from tests.unit.puppet_recorder_mocks import MockRecorderClient
from tg_auto_test.demo_ui.puppet_recorder.recorder_server import PuppetRecorderServer, create_puppet_recorder_app
from tg_auto_test.demo_ui.server.demo_server import DemoClientProtocol
from tg_auto_test.test_utils.models import ServerlessMessage


class TestPuppetRecorderServer:
    """Tests for PuppetRecorderServer initialization."""

    def test_init_with_valid_peer(self) -> None:
        mock_client = MagicMock()
        server = PuppetRecorderServer(cast(DemoClientProtocol, mock_client), "test_bot")
        assert server.peer == "test_bot"
        assert server.timeout == 10.0
        assert not server.session.is_recording

    def test_init_with_empty_peer_fails(self) -> None:
        mock_client = MagicMock()
        with pytest.raises(ValueError, match="Peer must be specified"):
            PuppetRecorderServer(cast(DemoClientProtocol, mock_client), "")

    def test_init_with_custom_timeout(self) -> None:
        mock_client = MagicMock()
        server = PuppetRecorderServer(cast(DemoClientProtocol, mock_client), "test_bot", timeout=30.0)
        assert server.timeout == 30.0

    def test_create_app_returns_fastapi(self) -> None:
        mock_client = MagicMock()
        server = PuppetRecorderServer(cast(DemoClientProtocol, mock_client), "test_bot")
        app = server.create_app()
        assert hasattr(app, "state")


def test_factory_function() -> None:
    mock_client = MagicMock()
    app = create_puppet_recorder_app(client=cast(DemoClientProtocol, mock_client), peer="test_bot")
    assert hasattr(app, "state")


def test_factory_function_validates_peer() -> None:
    mock_client = MagicMock()
    with pytest.raises(ValueError, match="Peer must be specified"):
        create_puppet_recorder_app(client=cast(DemoClientProtocol, mock_client), peer="")


class TestRecordingControlRoutes:
    """Tests for recording start/stop/clear/status routes."""

    def _make_app(self) -> TestClient:
        mock_client = MockRecorderClient()
        server = PuppetRecorderServer(cast(DemoClientProtocol, mock_client), "test_bot")
        return TestClient(server.create_app())

    def test_recording_status_initially_off(self) -> None:
        client = self._make_app()
        resp = client.get("/api/recording/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["recording"] is False
        assert data["step_count"] == 0

    def test_start_recording(self) -> None:
        client = self._make_app()
        resp = client.post("/api/recording/start")
        assert resp.status_code == 200
        assert resp.json()["recording"] is True
        status = client.get("/api/recording/status").json()
        assert status["recording"] is True

    def test_stop_recording(self) -> None:
        client = self._make_app()
        client.post("/api/recording/start")
        resp = client.post("/api/recording/stop")
        assert resp.status_code == 200
        assert resp.json()["recording"] is False

    def test_clear_recording(self) -> None:
        client = self._make_app()
        client.post("/api/recording/start")
        client.post("/api/message", json={"text": "hello"})
        client.post("/api/recording/clear")
        status = client.get("/api/recording/status").json()
        assert status["step_count"] == 0
        assert status["recording"] is False

    def test_steps_empty_initially(self) -> None:
        client = self._make_app()
        resp = client.get("/api/recording/steps")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_export_empty_session(self) -> None:
        client = self._make_app()
        resp = client.get("/api/recording/export")
        assert resp.status_code == 200
        assert "async def test_recorded_session" in resp.text
        assert "no steps recorded" in resp.text


class TestRecordingMessageRoutes:
    """Tests for message routes with recording."""

    def _make_app(self, response: ServerlessMessage | None = None) -> TestClient:
        mock_client = MockRecorderClient(response)
        server = PuppetRecorderServer(cast(DemoClientProtocol, mock_client), "test_bot")
        return TestClient(server.create_app())

    def test_send_message_records_step(self) -> None:
        test_client = self._make_app(ServerlessMessage(id=1, text="echo"))
        test_client.post("/api/recording/start")
        resp = test_client.post("/api/message", json={"text": "hello"})
        assert resp.status_code == 200
        assert resp.json()[0]["text"] == "echo"
        steps = test_client.get("/api/recording/steps").json()
        assert len(steps) == 1
        assert steps[0]["action"] == "send_message"
        assert steps[0]["text"] == "hello"

    def test_send_message_not_recorded_when_stopped(self) -> None:
        test_client = self._make_app()
        test_client.post("/api/message", json={"text": "hello"})
        steps = test_client.get("/api/recording/steps").json()
        assert len(steps) == 0

    def test_multiple_messages_recorded(self) -> None:
        test_client = self._make_app(ServerlessMessage(id=1, text="reply"))
        test_client.post("/api/recording/start")
        test_client.post("/api/message", json={"text": "/start"})
        test_client.post("/api/message", json={"text": "hello"})
        steps = test_client.get("/api/recording/steps").json()
        assert len(steps) == 2
        assert steps[0]["text"] == "/start"
        assert steps[1]["text"] == "hello"

    def test_export_after_recording(self) -> None:
        test_client = self._make_app(ServerlessMessage(id=1, text="Welcome!"))
        test_client.post("/api/recording/start")
        test_client.post("/api/message", json={"text": "/start"})
        resp = test_client.get("/api/recording/export")
        assert 'send_message("/start")' in resp.text
        assert 'assert response.text == "Welcome!"' in resp.text

    def test_reset_does_not_clear_recording(self) -> None:
        test_client = self._make_app(ServerlessMessage(id=1, text="echo"))
        test_client.post("/api/recording/start")
        test_client.post("/api/message", json={"text": "hi"})
        test_client.post("/api/reset")
        steps = test_client.get("/api/recording/steps").json()
        assert len(steps) == 1
