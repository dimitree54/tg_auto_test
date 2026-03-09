from collections import deque

from tg_auto_test.test_utils.models import ServerlessMessage


def remove_message(outbox: deque[ServerlessMessage], message_id: int) -> None:
    for index, existing in enumerate(outbox):
        if existing.id == message_id:
            del outbox[index]
            return


def pop_message_by_id(outbox: deque[ServerlessMessage], message_id: int) -> ServerlessMessage | None:
    for index, existing in enumerate(outbox):
        if existing.id == message_id:
            message = outbox[index]
            del outbox[index]
            return message
    return None
