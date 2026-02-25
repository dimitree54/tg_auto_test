"""API request and response models for the demo server."""

from pydantic import BaseModel


class TextMessageRequest(BaseModel):
    text: str


class InvoicePayRequest(BaseModel):
    message_id: int


class CallbackRequest(BaseModel):
    message_id: int
    data: str


class BotCommandInfo(BaseModel):
    command: str
    description: str


class BotStateResponse(BaseModel):
    commands: list[BotCommandInfo]
    menu_button_type: str


class PollVoteRequest(BaseModel):
    message_id: int
    option_ids: list[int]


class MessageResponse(BaseModel):
    type: str  # "text" | "invoice" | "document" | "voice" | "photo" | "video_note" | "poll"
    text: str = ""
    file_id: str = ""
    filename: str = ""
    message_id: int = 0
    title: str = ""
    description: str = ""
    currency: str = ""
    total_amount: int = 0
    reply_markup: dict | None = None
    poll_question: str = ""
    poll_options: list[dict[str, int | str]] = []
    poll_id: str = ""
    entities: list[dict[str, str | int]] = []
