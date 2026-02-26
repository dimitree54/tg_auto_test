"""Tests for test code generation from recorded puppet sessions."""

from tg_auto_test.demo_ui.puppet_recorder.recorder_models import RecordedStep
from tg_auto_test.demo_ui.puppet_recorder.test_codegen import generate_test_code


def _step(action: str = "send_message", **kwargs: str | int | tuple[int, ...]) -> RecordedStep:
    return RecordedStep(action=action, **kwargs)  # type: ignore[arg-type]


class TestEmptyAndBasic:
    """Tests for empty sessions and basic code generation."""

    def test_empty_session_produces_stub(self) -> None:
        code = generate_test_code([])
        assert "async def test_recorded_session" in code
        assert "no steps recorded" in code

    def test_custom_test_name(self) -> None:
        assert "async def test_my_bot" in generate_test_code([], test_name="test_my_bot")

    def test_has_imports_and_structure(self) -> None:
        code = generate_test_code([_step(text="x", response_type="text", response_text="y")])
        assert "import pytest" in code
        assert "ServerlessTelegramClient" in code
        assert "try:" in code
        assert "finally:" in code
        assert "await client.disconnect()" in code


class TestSendMessage:
    """Tests for send_message step code generation."""

    def test_single_text_message(self) -> None:
        code = generate_test_code([_step(text="hello", response_type="text", response_text="hello")])
        assert 'await conv.send_message("hello")' in code
        assert 'assert response.text == "hello"' in code

    def test_command_message(self) -> None:
        code = generate_test_code([_step(text="/start", response_type="text", response_text="Welcome!")])
        assert 'send_message("/start")' in code
        assert 'assert response.text == "Welcome!"' in code

    def test_multiple_messages(self) -> None:
        steps = [
            _step(text="/start", response_type="text", response_text="Welcome!"),
            _step(text="hi", response_type="text", response_text="hi"),
        ]
        assert generate_test_code(steps).count("await conv.get_response()") == 2

    def test_non_text_response(self) -> None:
        code = generate_test_code([_step(text="/photo", response_type="photo")])
        assert "assert response.photo is not None" in code

    def test_string_escaping(self) -> None:
        code = generate_test_code([_step(text='say "hi"', response_type="text", response_text='said "bye"')])
        assert 'say \\"hi\\"' in code
        assert 'said \\"bye\\"' in code

    def test_newline_escaping(self) -> None:
        code = generate_test_code([_step(text="line1\nline2", response_type="text", response_text="ok")])
        assert "line1\\nline2" in code


class TestSendFile:
    """Tests for send_file step code generation."""

    def test_photo_with_caption(self) -> None:
        code = generate_test_code([_step("send_file", file_type="photo", caption="pic", response_type="text")])
        assert 'caption="pic"' in code
        assert "# Send a photo file" in code

    def test_document(self) -> None:
        assert "force_document=True" in generate_test_code([
            _step("send_file", file_type="document", response_type="text")
        ])

    def test_voice(self) -> None:
        assert "voice_note=True" in generate_test_code([_step("send_file", file_type="voice", response_type="text")])

    def test_video_note(self) -> None:
        assert "video_note=True" in generate_test_code([
            _step("send_file", file_type="video_note", response_type="text")
        ])


class TestInteractive:
    """Tests for click_button, pay_invoice, and poll_vote code generation."""

    def test_click_button(self) -> None:
        code = generate_test_code([
            _step("click_button", callback_data="opt_a", message_id=5, response_type="text", response_text="Chosen"),
        ])
        assert 'callback_data="opt_a"' in code
        assert "ids=5" in code
        assert 'assert response.text == "Chosen"' in code

    def test_pay_invoice(self) -> None:
        code = generate_test_code([_step("pay_invoice", message_id=10, response_type="text", response_text="Paid!")])
        assert "Pay invoice on message 10" in code
        assert "Paid!" in code

    def test_poll_vote(self) -> None:
        code = generate_test_code([_step("poll_vote", message_id=7, option_ids=(0, 2), response_type="text")])
        assert "options [0, 2]" in code


class TestComplexSession:
    """Tests for complex multi-step sessions."""

    def test_full_flow(self) -> None:
        steps = [
            _step(text="/start", response_type="text", response_text="Welcome!"),
            _step(text="/inline", response_type="text", response_text="Choose:"),
            _step("click_button", callback_data="opt_a", message_id=2, response_type="text", response_text="Chosen"),
            _step(text="bye", response_type="text", response_text="bye"),
        ]
        code = generate_test_code(steps, test_name="test_full_flow")
        assert "async def test_full_flow" in code
        assert code.count("await conv.send_message") == 3
        assert code.count("await conv.get_response()") == 3
        assert "msg.click" in code
