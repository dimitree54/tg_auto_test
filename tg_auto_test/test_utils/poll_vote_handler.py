"""Poll vote handling for ServerlessTelegramClient."""

from typing import TYPE_CHECKING  # noqa: TID251

if TYPE_CHECKING:
    from tg_auto_test.test_utils.models import ServerlessMessage
    from tg_auto_test.test_utils.serverless_client_helpers import ServerlessClientHelpers

from tg_auto_test.test_utils.json_types import JsonValue


class PollTracker:
    """Tracks polls by message_id for SendVoteRequest handling."""

    def __init__(self) -> None:
        # Maps message_id -> (poll_id, option_index_to_bytes_mapping)
        self._polls_by_message: dict[int, tuple[str, dict[int, bytes]]] = {}

    def track_poll(self, message_id: int, poll_id: str, options_data: list[dict[str, str]]) -> None:
        """Track a poll by message_id when it's sent.

        Args:
            message_id: Message ID of the poll message
            poll_id: Poll ID string
            options_data: List of poll option dicts with 'text' field
        """
        # Create mapping from option index to bytes (consistent with model_helpers.py)
        option_mapping = {i: bytes([i]) for i in range(len(options_data))}
        self._polls_by_message[message_id] = (poll_id, option_mapping)

    def lookup_poll(self, message_id: int) -> tuple[str, dict[int, bytes]] | None:
        """Look up poll data by message_id.

        Returns:
            Tuple of (poll_id, option_mapping) or None if not found
        """
        return self._polls_by_message.get(message_id)

    def map_option_bytes_to_indices(self, option_bytes: list[bytes]) -> list[int]:
        """Map option bytes back to indices for any tracked poll.

        Args:
            option_bytes: List of bytes from SendVoteRequest.options

        Returns:
            List of option indices

        Raises:
            ValueError: If any option byte is not recognized
        """
        indices = []
        for opt_bytes in option_bytes:
            # Since we use bytes([i]), we can reverse map
            if len(opt_bytes) == 1 and 0 <= opt_bytes[0] < 256:
                indices.append(opt_bytes[0])
            else:
                raise ValueError(f"Unrecognized option bytes: {opt_bytes!r}")
        return indices


async def handle_send_vote_request_for_client(
    tracker: PollTracker,
    helpers: "ServerlessClientHelpers",
    process_update_fn: callable,
    outbox: object,
    message_id: int,
    option_bytes: list[bytes],
) -> "ServerlessMessage":
    """Handle SendVoteRequest for ServerlessTelegramClientCore."""
    outbox.clear()
    return await handle_send_vote_request(tracker, helpers, process_update_fn, message_id, option_bytes)


async def handle_send_vote_request(
    tracker: PollTracker,
    helpers: "ServerlessClientHelpers",
    process_update_fn: callable,
    message_id: int,
    option_bytes: list[bytes],
) -> "ServerlessMessage":
    """Handle SendVoteRequest by converting to poll_answer update.

    Args:
        tracker: PollTracker instance
        helpers: ServerlessClientHelpers instance
        process_update_fn: Function to process the poll_answer update
        message_id: Message ID from SendVoteRequest.msg_id
        option_bytes: Option bytes from SendVoteRequest.options

    Returns:
        ServerlessMessage with bot's response

    Raises:
        RuntimeError: If poll not found or processing fails
    """
    # Look up the poll by message_id
    poll_data = tracker.lookup_poll(message_id)
    if poll_data is None:
        raise RuntimeError(f"Poll not found for message_id {message_id}")

    poll_id, _option_mapping = poll_data

    # Convert option bytes to indices
    try:
        option_indices = tracker.map_option_bytes_to_indices(option_bytes)
    except ValueError as e:
        raise RuntimeError(f"Invalid option bytes for message_id {message_id}: {e}")

    # Build poll_answer update (same as the old process_poll_answer)
    payload = {
        "update_id": helpers.next_update_id_value(),
        "poll_answer": {
            "poll_id": poll_id,
            "user": helpers.user_dict(),
            "option_ids": option_indices,
        },
    }

    return await process_update_fn(payload)


def create_callback_query_payload(
    message_id: int, data: str, chat_id: int, bot_user: JsonValue, helpers: "ServerlessClientHelpers"
) -> dict[str, JsonValue]:
    """Create callback query payload for ServerlessTelegramClient."""
    callback_message: dict[str, JsonValue] = {
        "message_id": message_id,
        "date": 0,
        "chat": {"id": chat_id, "type": "private"},
        "from": bot_user,
        "text": "",
    }
    callback_query: dict[str, JsonValue] = {
        "id": f"cb_{message_id}_{data}",
        "from": helpers.user_dict(),
        "chat_instance": str(chat_id),
        "message": callback_message,
        "data": data,
    }
    payload: dict[str, JsonValue] = {
        "update_id": helpers.next_update_id_value(),
        "callback_query": callback_query,
    }
    return payload
