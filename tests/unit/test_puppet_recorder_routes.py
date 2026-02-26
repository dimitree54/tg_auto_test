"""Tests for puppet recorder file upload routes and export integration."""

import io
from typing import cast

from fastapi.testclient import TestClient

from tests.unit.puppet_recorder_mocks import MockRecorderClient
from tg_auto_test.demo_ui.puppet_recorder.recorder_server import PuppetRecorderServer
from tg_auto_test.demo_ui.server.demo_server import DemoClientProtocol
from tg_auto_test.test_utils.models import ServerlessMessage


class TestRecordingFileRoutes:
    """Tests for file upload routes with recording."""

    def _make_app(self) -> TestClient:
        response = ServerlessMessage(id=2, text="Got your file")
        mock_client = MockRecorderClient(response)
        server = PuppetRecorderServer(cast(DemoClientProtocol, mock_client), "test_bot")
        return TestClient(server.create_app())

    def test_send_document_records_step(self) -> None:
        test_client = self._make_app()
        test_client.post("/api/recording/start")
        resp = test_client.post("/api/document", files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")})
        assert resp.status_code == 200
        steps = test_client.get("/api/recording/steps").json()
        assert len(steps) == 1
        assert steps[0]["action"] == "send_file"
        assert steps[0]["file_type"] == "document"

    def test_send_photo_records_step_with_caption(self) -> None:
        test_client = self._make_app()
        test_client.post("/api/recording/start")
        resp = test_client.post(
            "/api/photo",
            files={"file": ("img.png", io.BytesIO(b"\x89PNG"), "image/png")},
            data={"caption": "my photo"},
        )
        assert resp.status_code == 200
        steps = test_client.get("/api/recording/steps").json()
        assert len(steps) == 1
        assert steps[0]["file_type"] == "photo"
        assert steps[0]["caption"] == "my photo"

    def test_send_voice_records_step(self) -> None:
        test_client = self._make_app()
        test_client.post("/api/recording/start")
        test_client.post("/api/voice", files={"file": ("voice.ogg", io.BytesIO(b"audio"), "audio/ogg")})
        steps = test_client.get("/api/recording/steps").json()
        assert len(steps) == 1
        assert steps[0]["file_type"] == "voice"

    def test_send_video_note_records_step(self) -> None:
        test_client = self._make_app()
        test_client.post("/api/recording/start")
        test_client.post("/api/video_note", files={"file": ("video.mp4", io.BytesIO(b"video"), "video/mp4")})
        steps = test_client.get("/api/recording/steps").json()
        assert len(steps) == 1
        assert steps[0]["file_type"] == "video_note"


class TestRecordingExportIntegration:
    """End-to-end tests verifying exported code quality."""

    def _make_app(self, response: ServerlessMessage) -> TestClient:
        mock_client = MockRecorderClient(response)
        server = PuppetRecorderServer(cast(DemoClientProtocol, mock_client), "test_bot")
        return TestClient(server.create_app())

    def test_full_session_export(self) -> None:
        test_client = self._make_app(ServerlessMessage(id=1, text="Welcome!"))
        test_client.post("/api/recording/start")
        test_client.post("/api/message", json={"text": "/start"})
        test_client.post("/api/message", json={"text": "hello"})
        test_client.post("/api/recording/stop")
        resp = test_client.get("/api/recording/export")
        code = resp.text
        assert "import pytest" in code
        assert "ServerlessTelegramClient" in code
        assert 'send_message("/start")' in code
        assert 'send_message("hello")' in code
        assert "await client.connect()" in code
        assert "await client.disconnect()" in code
        assert code.count("get_response") == 2

    def test_export_preserves_steps_after_stop(self) -> None:
        test_client = self._make_app(ServerlessMessage(id=1, text="ok"))
        test_client.post("/api/recording/start")
        test_client.post("/api/message", json={"text": "test"})
        test_client.post("/api/recording/stop")
        steps = test_client.get("/api/recording/steps").json()
        assert len(steps) == 1
        resp = test_client.get("/api/recording/export")
        assert 'send_message("test")' in resp.text
