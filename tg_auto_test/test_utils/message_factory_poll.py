"""Poll message builder for ServerlessMessage."""

from tg_auto_test.test_utils.message_factory_invoice import message_id_from_result
from tg_auto_test.test_utils.models import ServerlessMessage, TelegramApiCall


def build_poll_message(call: TelegramApiCall) -> ServerlessMessage:
    """Build a ServerlessMessage for a sendPoll API call."""
    message_id = message_id_from_result(call)

    if call.result is None:
        raise ValueError("Poll API call must have a result")

    if not isinstance(call.result, dict):
        raise ValueError("Poll API call result must be a dict")

    poll_data = call.result.get("poll")
    if poll_data is None:
        raise ValueError("Poll API call result must contain poll data")

    return ServerlessMessage(
        id=message_id,
        poll_data=poll_data,
    )
