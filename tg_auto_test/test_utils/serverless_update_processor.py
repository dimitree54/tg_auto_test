import asyncio
from collections import deque

from telegram import Update

from tg_auto_test.test_utils.exceptions import BotNoResponseError
from tg_auto_test.test_utils.json_types import JsonValue
from tg_auto_test.test_utils.models import ServerlessMessage, TelegramApiCall
from tg_auto_test.test_utils.response_processor import extract_responses


class ServerlessUpdateProcessor:
    """Handles update processing for serverless clients."""

    async def process_update(
        self,
        client: "ServerlessTelegramClientCore",
        payload: dict[str, JsonValue],
    ) -> list[TelegramApiCall]:
        if not client._connected:  # noqa: SLF001
            raise RuntimeError("Call connect() before processing payloads.")
        calls_before = len(client._request.calls)  # noqa: SLF001
        update = Update.de_json(payload, client._application.bot)  # noqa: SLF001
        await client._application.process_update(update)  # noqa: SLF001
        return client._request.calls[calls_before:]  # noqa: SLF001

    async def process_message_update(
        self,
        client: "ServerlessTelegramClientCore",
        payload: dict[str, JsonValue],
    ) -> ServerlessMessage:
        calls_before = len(client._request.calls)  # noqa: SLF001
        tasks_before = _snapshot_tasks()
        await self.process_update(client, payload)
        responses = _extract_client_responses(client, calls_before)
        if not responses:
            pending_tasks = _snapshot_tasks() - tasks_before
            if pending_tasks:
                await _await_tasks(pending_tasks)
                responses = _extract_client_responses(client, calls_before)
        if not responses:
            raise BotNoResponseError(
                "Bot did not respond to the message. It may not have a handler for this message type."
            )
        if getattr(client, "_live_message_capture", False):
            return responses[-1]
        new_calls = client._request.calls[calls_before:]  # noqa: SLF001
        for resp in responses:
            if resp._is_edit:  # noqa: SLF001
                _replace_edited_message(client._outbox, resp)  # noqa: SLF001
                client._edit_outbox.append(resp)  # noqa: SLF001
            else:
                client._outbox.append(resp)  # noqa: SLF001
        _apply_deletions(new_calls, client._outbox)  # noqa: SLF001
        return responses[-1]


def _extract_client_responses(
    client: "ServerlessTelegramClientCore",
    calls_before: int,
) -> list[ServerlessMessage]:
    return extract_responses(
        client._request.calls[calls_before:],  # noqa: SLF001
        client._request.file_store,  # noqa: SLF001
        client._invoices,
        client._handle_click,
        client._poll_tracker,  # noqa: SLF001
    )


async def _await_tasks(tasks: set[asyncio.Task[object]]) -> None:
    await asyncio.gather(*tasks)


def _snapshot_tasks() -> set[asyncio.Task[object]]:
    current_task = asyncio.current_task()
    return {task for task in asyncio.all_tasks() if task is not current_task and not task.done()}


def _apply_deletions(
    calls: list[TelegramApiCall],
    outbox: deque[ServerlessMessage],
) -> None:
    for call in calls:
        if call.api_method != "deleteMessage":
            continue
        msg_id = int(call.parameters["message_id"])
        for i, existing in enumerate(outbox):
            if existing.id == msg_id:
                del outbox[i]
                break


def _replace_edited_message(
    outbox: deque[ServerlessMessage],
    edited: ServerlessMessage,
) -> None:
    for i, existing in enumerate(outbox):
        if existing.id == edited.id:
            outbox[i] = edited
            return
