# TASK_01 — Add /poll command and PollAnswerHandler to proto_tg_bot

**Repo:** `/Users/yid/source/proto_tg_bot`
**Dependencies:** None

## Description

Add a `/poll` command to the bot that sends a poll and a `PollAnswerHandler` that echoes the user's vote. Write integration and e2e tests exercising the full flow. The serverless tests are **expected to fail** at this point because `tg-auto-test` does not yet handle `sendPoll` — that is intentional and will be resolved by TASK_02–05.

### /poll command behaviour

1. User sends `/poll`.
2. Bot calls `sendPoll` with:
   - `question`: `"What's your favorite color?"`
   - `options`: `["Red", "Green", "Blue"]`
   - `is_anonymous`: `False` (required for `PollAnswerHandler` to fire)
3. Bot registers a `PollAnswerHandler`.
4. When a user votes, the handler sends a text message: `"You voted for: <option>"` (comma-separated if multiple).

### Implementation detail

- `PollAnswerHandler` must be registered in `build_application` (not dynamically per-poll) so it is always active.
- The handler receives a `PollAnswer` update. It should use `context.bot.send_message` to reply (since `PollAnswer` updates have no `message` to reply to — use `poll_answer.user.id` as `chat_id`).
- Store the poll options in `context.bot_data` keyed by `poll_id` (populated in the `/poll` handler after `sendPoll` returns the `poll.id`).

## Files to modify/create

| File | Action |
|------|--------|
| `proto_tg_bot/bot.py` | Add `poll_handler`, `poll_answer_handler`, register both handlers + `PollAnswerHandler` |
| `tests/integration/test_poll.py` | New — serverless integration tests for `/poll` and poll answer |
| `tests/e2e/test_bot_e2e.py` | Add an e2e test for the `/poll` flow (or create `tests/e2e/test_poll_e2e.py`) |

## Acceptance Criteria

1. `/poll` command handler exists and calls `message.reply_poll(...)`.
2. `PollAnswerHandler` is registered in `build_application`.
3. `poll_answer_handler` reads the voted option(s) from `context.bot_data` and sends `"You voted for: <option>"`.
4. Integration test `test_poll.py` exists and exercises:
   - Sending `/poll` and asserting the response contains poll data.
   - Simulating a poll answer and asserting the echo text.
5. E2e test exists with the same assertions.
6. `make check` passes **except** for the poll-specific serverless tests which fail with `AssertionError: Unexpected Telegram API method: sendPoll`. This is expected and documented in test markers/comments.
7. All non-poll tests remain green.

## Risks / Notes

- The poll integration tests should use `pytest.mark.xfail(reason="tg-auto-test does not support sendPoll yet")` so that `make check` stays green overall. Remove the xfail in TASK_05.
- PTB's `PollAnswerHandler` receives updates with `update.poll_answer` (not `update.message`). The handler must use `context.bot.send_message(chat_id=poll_answer.user.id, ...)` to respond.
- `message.reply_poll` returns a `Message` object with a `.poll` attribute containing `poll.id` — store this for the answer handler lookup.
