---
Task ID: `T2`
Title: `Add behavioral parity tests for core conversation patterns`
Sprint: `2026-03-06_qa-improvements`
Module: `tests/unit`
Depends on: `--`
Parallelizable: `yes, with T1 and T3`
Owner: `Developer`
Status: `planned`
---

## Goal / value

A new test file verifies that the most common Telethon conversation patterns produce
correct behavioral outcomes in serverless mode. This closes the gap where signature
conformance passes but the runtime behavior diverges (e.g., `get_edit()` was stubbed
with `NotImplementedError` even though the plumbing existed).

## Context (contract mapping)

- Requirements: `CONTRIBUTING.md` ("We re-implement, not invent", "Single chat scope")
- Existing behavioral tests: `tests/unit/test_click_returns_message_bug.py` (pattern: send -> click -> get_response)
- Existing behavioral tests: `tests/unit/test_get_edit_bug.py` (pattern: send -> get_response -> get_edit)
- Existing text tests: `tests/unit/test_serverless_client_text.py` (basic send -> get_response)

## Preconditions

- `python-telegram-bot >= 22.6` installed (already in `pyproject.toml`)
- Understanding of PTB handler wiring (`CommandHandler`, `CallbackQueryHandler`, `MessageHandler`)

## Non-goals

- Testing media patterns (photos, documents, voice) - already covered by existing tests
- Testing payment/Stars patterns - already covered by existing tests
- Testing error scenarios (those belong in separate regression tests)
- Modifying any source code to make tests pass

## Module boundary constraints (STRICTLY ENFORCED)

**ALLOWED - this task may ONLY touch:**
- `tests/unit/test_behavioral_parity.py` - new test file
- `vulture_whitelist.py` - only if vulture raises false positives on new symbols

**FORBIDDEN - this task must NEVER touch:**
- `tg_auto_test/` source code
- Existing test files
- Linter configuration

**Test scope:**
- Tests go in: `tests/unit/`
- Test command: `uv run pytest tests/unit/test_behavioral_parity.py -x -v`
- Full validation: `make check`

## Touched surface (expected files / modules)

- `tests/unit/test_behavioral_parity.py` (new)

## Dependencies and sequencing notes

- No dependencies on T1 or T3
- Can run in parallel with both

## Third-party / library research

- **Library**: `python-telegram-bot` 22.6+
  - `CommandHandler` - matches commands like `/start`
  - `CallbackQueryHandler` - matches inline button presses
  - `MessageHandler` with `filters.TEXT` - matches text messages
  - `Update.callback_query.answer()` - acknowledges callback query
  - `Update.callback_query.message.reply_text()` - sends response after callback
  - `Message.edit_text()` - edits an existing message
  - Reference: https://docs.python-telegram-bot.org/en/v22.6/

- **Library**: `telethon` 1.42+ (interface being faked)
  - `Conversation.send_message()` -> `Message` (outbox message)
  - `Conversation.get_response()` -> `Message` (next bot reply)
  - `Conversation.get_edit()` -> `Message` (next edit to a bot message)
  - `Message.click(data=...)` -> `BotCallbackAnswer` (callback acknowledgement)
  - Reference: https://docs.telethon.dev/en/stable/modules/client.html#telethon.client.messages.MessageMethods

## Implementation steps

1. **Create `tests/unit/test_behavioral_parity.py`.**

2. **Define self-contained PTB handlers within the test file** (do NOT import from `helpers_ptb_app.py` to keep the test self-contained and avoid coupling):

   a. **Echo handler**: replies with the same text
   b. **Status-then-edit handler**: sends "Loading...", then edits to "Done!"
   c. **Inline-button handler**: sends message with inline keyboard
   d. **Callback handler**: answers callback query, then sends a follow-up message

3. **Define a build function** for each test pattern that wires only the handlers needed.

4. **Write the four behavioral pattern tests:**

   a. **`test_send_response_pattern`** (send -> get_response):
      - `conv.send_message("hello")` -> `conv.get_response()` returns "hello"
      - Verifies the most basic Telethon conversation pattern

   b. **`test_send_edit_pattern`** (send -> get_response -> get_edit):
      - `conv.send_message("/work")` -> `conv.get_response()` returns message
      - `conv.get_edit()` returns the edited text "Done!"
      - `get_edit().id == get_response().id` (same message was edited)

   c. **`test_click_callback_pattern`** (send -> get_response -> click -> get_response):
      - `conv.send_message("/menu")` -> `conv.get_response()` returns message with buttons
      - `msg.click(data=b"go")` returns `ServerlessBotCallbackAnswer` (NOT `ServerlessMessage`)
      - `conv.get_response()` returns the bot's follow-up message (not consumed by click)

   d. **`test_outbox_isolation_pattern`** (send clears previous outbox):
      - `conv.send_message("first")` -> `conv.get_response()` returns "first"
      - `conv.send_message("second")` -> `conv.get_response()` returns "second"
      - The second `get_response()` must NOT return "first" (outbox was cleared by second `send_message`)

5. **Add edge-case tests:**

   e. **`test_get_response_after_edit_returns_edited_text`**:
      - When bot sends "Loading..." then edits to "Done!", `get_response()` returns the
        final text "Done!" (the response reflects the last state)

   f. **`test_click_returns_bot_callback_answer_type`**:
      - Explicitly verify `isinstance(result, ServerlessBotCallbackAnswer)` after `click(data=...)`

6. **Ensure file stays under 200 lines.** The handlers + 6 tests + build functions will be
   tight. Strategies to stay compact:
   - Combine build functions using parameters
   - Use a single multi-handler app builder
   - If over ~180 lines, split into `test_behavioral_parity.py` (tests) and reuse
     existing handlers from `helpers_ptb_app.py` where possible

7. **Run `make check`** to verify all quality gates pass.

## Production safety constraints

N/A - test-only file, no runtime or database impact.

## Anti-disaster constraints

- **Reuse before build**: Reuse the `ServerlessTelegramClient` + `conversation()` pattern from existing tests
- **Correct libraries only**: Only PTB and pytest - no new dependencies
- **Correct file locations**: `tests/unit/test_behavioral_parity.py`
- **No regressions**: New tests only; existing tests untouched

## Error handling + correctness rules

- Every test must explicitly `await client.disconnect()` in a `finally` block
- No bare `except` or swallowed exceptions
- Use `pytest.raises` for expected `NotImplementedError` cases if testing negative paths
- Assert specific values, not just truthiness

## Zero legacy tolerance rule

- No commented-out tests
- No placeholder assertions
- No duplicate handler definitions (reuse if possible)

## Acceptance criteria (testable)

1. `tests/unit/test_behavioral_parity.py` exists
2. Send -> get_response pattern test passes
3. Send -> get_response -> get_edit pattern test passes
4. Send -> click -> get_response pattern test passes (click returns `ServerlessBotCallbackAnswer`)
5. Outbox isolation test passes (second send_message clears first outbox)
6. `uv run pytest tests/unit/test_behavioral_parity.py -x -v` passes
7. `make check` passes 100%
8. File is under 200 lines

## Verification / quality gates

- [ ] New test file created in `tests/unit/`
- [ ] Tests pass: `uv run pytest tests/unit/test_behavioral_parity.py -x -v`
- [ ] `make check` passes 100%
- [ ] File under 200 lines (pylint C0302)
- [ ] No new vulture warnings (or whitelist updated)
- [ ] No ruff violations
- [ ] Tests use real PTB handlers (not mocks)

## Edge cases

- Bot handler that sends multiple messages in response to one input (outbox has multiple items)
- Bot handler that edits a message but also sends a new one (both edit_outbox and outbox have items)
- `get_response()` called when outbox is empty (should raise - verify the error)
- `get_edit()` called when no edit has occurred (should raise - verify the error)

## Notes / risks

- **Risk**: Handler wiring inside tests may duplicate logic from `helpers_ptb_app.py`.
  - **Mitigation**: Intentional - self-contained tests are more reliable than coupling to shared helpers. The patterns tested here are specific behavioral contracts, not generic functionality.
- **Risk**: Test file may approach 200-line limit with 6 tests + handlers.
  - **Mitigation**: If needed, use a shared `_build_app` that registers all handlers and select behavior via different commands. This avoids per-test builder functions.
