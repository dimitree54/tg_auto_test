"""Data models for the puppet recorder: recorded steps and recording sessions."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RecordedStep:
    """A single recorded user action and the bot's response."""

    action: str  # "send_message" | "send_file" | "click_button" | "pay_invoice" | "poll_vote"
    # Input fields (relevant based on action)
    text: str = ""
    file_type: str = ""  # "photo" | "document" | "voice" | "video_note"
    caption: str = ""
    callback_data: str = ""
    message_id: int = 0
    option_ids: tuple[int, ...] = ()
    # Response fields
    response_type: str = ""
    response_text: str = ""
    response_message_id: int = 0


class RecordingSession:
    """Manages a list of recorded steps during a puppet recorder session."""

    def __init__(self) -> None:
        self._steps: list[RecordedStep] = []
        self._recording: bool = False

    @property
    def steps(self) -> list[RecordedStep]:
        """Return a copy of all recorded steps."""
        return list(self._steps)

    @property
    def is_recording(self) -> bool:
        """Whether recording is currently active."""
        return self._recording

    @property
    def step_count(self) -> int:
        """Number of steps recorded so far."""
        return len(self._steps)

    def start(self) -> None:
        """Start recording. Clears any previous steps."""
        self._steps.clear()
        self._recording = True

    def stop(self) -> None:
        """Stop recording. Steps are preserved for export."""
        self._recording = False

    def clear(self) -> None:
        """Clear all recorded steps and stop recording."""
        self._steps.clear()
        self._recording = False

    def add_step(self, step: RecordedStep) -> None:
        """Add a step if recording is active. Ignored if not recording."""
        if self._recording:
            self._steps.append(step)
