# TASK_03 — Add process_poll_answer to ServerlessTelegramClientCore

**Repo:** `/Users/yid/source/tg_auto_test`
**Dependencies:** TASK_02

## Description

Add a `process_poll_answer(poll_id, option_ids)` method to `ServerlessTelegramClientCore` that simulates a user voting on a poll. This enables consumers (like `proto_tg_bot`) to test `PollAnswerHandler` flows in serverless mode.

### How Telegram delivers poll answers

When a user votes on a non-anonymous poll, Telegram sends an `Update` with a `poll_answer` field:

```json
{
  "update_id": 12345,
  "poll_answer": {
    "poll_id": "poll_1",
    "user": {"id": 9001, "is_bot": false, "first_name": "Alice"},
    "option_ids": [0]
  }
}
```

PTB routes this to any registered `PollAnswerHandler`. The handler typically uses `context.bot.send_message(chat_id=user.id, ...)` to respond.

### Implementation

Add to `ServerlessTelegramClientCore`:

```python
async def process_poll_answer(self, poll_id: str, option_ids: list[int]) -> ServerlessMessage:
    self._outbox.clear()
    payload = {
        "update_id": self._helpers.next_update_id_value(),
        "poll_answer": {
            "poll_id": poll_id,
            "user": self._helpers.user_dict(),
            "option_ids": option_ids,
        },
    }
    return await self._process_message_update(payload)
```

### Poll ID tracking

The consumer needs to know the `poll_id` to pass to `process_poll_answer`. There are two approaches:

**Option A — consumer reads poll_id from ServerlessMessage.poll:**
After `process_text_message("/poll")`, the consumer reads `response.poll.poll.id` to get the poll_id. This is the cleanest approach and matches how a real Telegram flow works.

**Option B — client tracks polls internally:**
The client maintains a `_polls` dict mapping `poll_id -> poll_data`, populated when `sendPoll` responses are processed. This provides a `last_poll_id` convenience property.

Prefer Option A for simplicity. Option B can be added if consumer ergonomics demand it.

### File size concern

`serverless_telegram_client_core.py` is at 190 lines. Adding `process_poll_answer` will exceed 200. Extract a group of related methods into a helper or refactor to stay under the limit. Possible extractions:
- Move `process_file_message` to a separate mixin or the helpers module.
- Move `process_callback_query` and `_handle_click` to a separate mixin.

## Files to modify/create

| File | Action |
|------|--------|
| `tg_auto_test/test_utils/serverless_telegram_client_core.py` | Add `process_poll_answer` method (with refactoring to stay under 200 lines) |
| `tg_auto_test/test_utils/serverless_telegram_client.py` | Expose `process_poll_answer` if needed (it may be inherited) |
| `tests/unit/test_serverless_client_poll.py` | Add tests for `process_poll_answer` (extend file from TASK_02 or create new) |

## Acceptance Criteria

1. `process_poll_answer(poll_id, option_ids)` exists on `ServerlessTelegramClientCore`.
2. Calling it constructs a valid PTB `Update` with `poll_answer` and dispatches it through `application.process_update`.
3. If the bot has a `PollAnswerHandler` registered, it fires and can send a response message.
4. The returned `ServerlessMessage` contains the bot's reply text.
5. Unit test demonstrates end-to-end: register a simple bot with `/poll` + `PollAnswerHandler` → send `/poll` → extract poll_id → `process_poll_answer(poll_id, [0])` → assert response text.
6. All files stay under 200 lines.
7. `make check` is 100% green.

## Risks / Notes

- `PollAnswer` updates do NOT contain a `message` field. PTB's `PollAnswerHandler` receives the update differently than `MessageHandler`. The constructed payload must match Telegram's schema exactly.
- The bot's `PollAnswerHandler` callback typically uses `context.bot.send_message(chat_id=..., text=...)` to respond (not `update.message.reply_text`). The `_process_message_update` pipeline already handles `sendMessage` calls from the bot, so this should work.
- If the bot stores poll options in `context.bot_data[poll_id]`, the `/poll` command must have run first to populate it. Tests must call `/poll` before `process_poll_answer`.
- `serverless_telegram_client_core.py` is at the 200-line limit — refactoring is mandatory, not optional.
