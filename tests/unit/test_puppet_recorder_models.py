"""Tests for puppet recorder data models."""

from tg_auto_test.demo_ui.puppet_recorder.recorder_models import RecordedStep, RecordingSession


class TestRecordedStep:
    """Tests for the RecordedStep dataclass."""

    def test_create_send_message_step(self) -> None:
        step = RecordedStep(
            action="send_message",
            text="hello",
            response_type="text",
            response_text="hello",
            response_message_id=1,
        )
        assert step.action == "send_message"
        assert step.text == "hello"
        assert step.response_type == "text"
        assert step.response_text == "hello"
        assert step.response_message_id == 1

    def test_create_send_file_step(self) -> None:
        step = RecordedStep(
            action="send_file",
            file_type="photo",
            caption="my photo",
            response_type="photo",
            response_message_id=2,
        )
        assert step.action == "send_file"
        assert step.file_type == "photo"
        assert step.caption == "my photo"
        assert step.response_type == "photo"

    def test_create_click_button_step(self) -> None:
        step = RecordedStep(
            action="click_button",
            callback_data="opt_a",
            message_id=5,
            response_type="text",
            response_text="You chose: opt_a",
        )
        assert step.action == "click_button"
        assert step.callback_data == "opt_a"
        assert step.message_id == 5

    def test_create_pay_invoice_step(self) -> None:
        step = RecordedStep(
            action="pay_invoice",
            message_id=10,
            response_type="text",
            response_text="Payment received!",
        )
        assert step.action == "pay_invoice"
        assert step.message_id == 10

    def test_create_poll_vote_step(self) -> None:
        step = RecordedStep(
            action="poll_vote",
            message_id=7,
            option_ids=(0, 1),
            response_type="text",
            response_text="You voted",
        )
        assert step.action == "poll_vote"
        assert step.option_ids == (0, 1)

    def test_defaults(self) -> None:
        step = RecordedStep(action="send_message")
        assert step.text == ""
        assert step.file_type == ""
        assert step.caption == ""
        assert step.callback_data == ""
        assert step.message_id == 0
        assert step.option_ids == ()
        assert step.response_type == ""
        assert step.response_text == ""
        assert step.response_message_id == 0

    def test_frozen(self) -> None:
        step = RecordedStep(action="send_message", text="hi")
        try:
            step.text = "bye"  # type: ignore[misc]
            raise AssertionError("Should have raised FrozenInstanceError")
        except AttributeError:
            pass


class TestRecordingSession:
    """Tests for the RecordingSession class."""

    def test_initial_state(self) -> None:
        session = RecordingSession()
        assert not session.is_recording
        assert session.step_count == 0
        assert session.steps == []

    def test_start_recording(self) -> None:
        session = RecordingSession()
        session.start()
        assert session.is_recording

    def test_stop_recording(self) -> None:
        session = RecordingSession()
        session.start()
        session.stop()
        assert not session.is_recording

    def test_add_step_while_recording(self) -> None:
        session = RecordingSession()
        session.start()
        step = RecordedStep(action="send_message", text="hello", response_type="text", response_text="hello")
        session.add_step(step)
        assert session.step_count == 1
        assert session.steps[0].text == "hello"

    def test_add_step_while_not_recording_is_ignored(self) -> None:
        session = RecordingSession()
        step = RecordedStep(action="send_message", text="hello")
        session.add_step(step)
        assert session.step_count == 0

    def test_clear_resets_everything(self) -> None:
        session = RecordingSession()
        session.start()
        session.add_step(RecordedStep(action="send_message", text="a"))
        session.add_step(RecordedStep(action="send_message", text="b"))
        assert session.step_count == 2

        session.clear()
        assert session.step_count == 0
        assert not session.is_recording

    def test_start_clears_previous_steps(self) -> None:
        session = RecordingSession()
        session.start()
        session.add_step(RecordedStep(action="send_message", text="old"))
        session.stop()
        assert session.step_count == 1

        session.start()
        assert session.step_count == 0

    def test_steps_returns_copy(self) -> None:
        session = RecordingSession()
        session.start()
        session.add_step(RecordedStep(action="send_message", text="x"))

        steps = session.steps
        steps.clear()
        assert session.step_count == 1

    def test_multiple_steps(self) -> None:
        session = RecordingSession()
        session.start()
        session.add_step(RecordedStep(action="send_message", text="/start"))
        session.add_step(RecordedStep(action="send_message", text="hello"))
        session.add_step(RecordedStep(action="click_button", callback_data="opt_a", message_id=1))
        assert session.step_count == 3
        assert session.steps[0].text == "/start"
        assert session.steps[1].text == "hello"
        assert session.steps[2].callback_data == "opt_a"

    def test_stop_preserves_steps(self) -> None:
        session = RecordingSession()
        session.start()
        session.add_step(RecordedStep(action="send_message", text="keep"))
        session.stop()
        assert session.step_count == 1
        assert session.steps[0].text == "keep"

    def test_add_after_stop_is_ignored(self) -> None:
        session = RecordingSession()
        session.start()
        session.add_step(RecordedStep(action="send_message", text="recorded"))
        session.stop()
        session.add_step(RecordedStep(action="send_message", text="ignored"))
        assert session.step_count == 1
