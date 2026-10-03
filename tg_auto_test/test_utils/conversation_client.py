from collections import deque
from pathlib import Path
from typing import Protocol, Unpack

from tg_auto_test.test_utils.file_send_options import FileSendOptions
from tg_auto_test.test_utils.models import ServerlessMessage
from tg_auto_test.test_utils.poll_vote_handler import PollTracker
from tg_auto_test.test_utils.serverless_bot_callback_answer import ServerlessBotCallbackAnswer
from tg_auto_test.test_utils.serverless_client_helpers import ServerlessClientHelpers
from tg_auto_test.test_utils.serverless_update_processor import ServerlessUpdateProcessor
from tg_auto_test.test_utils.stub_request import StubTelegramRequest


class ConversationClient(Protocol):
    _chat_id: int
    _edit_outbox: deque[ServerlessMessage]
    _helpers: ServerlessClientHelpers
    _invoices: dict[int, dict[str, object]]
    _outbox: deque[ServerlessMessage]
    _poll_tracker: PollTracker | None
    _request: StubTelegramRequest
    _update_processor: ServerlessUpdateProcessor

    async def _process_file_message(
        self, file: Path | bytes, **options: Unpack[FileSendOptions]
    ) -> ServerlessMessage: ...

    async def _handle_click(self, message_id: int, data: str) -> ServerlessBotCallbackAnswer: ...
