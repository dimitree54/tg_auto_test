---
Task ID: `T6`
Title: `Add cancel, cancel_all, wait_event, wait_read, mark_read to ServerlessTelegramConversation`
Depends on: —
Parallelizable: yes, with T1, T2, T3, T4, T5
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Add 5 missing conversation methods so that the 5 conversation conformance tests pass. Remove 5 xfail markers. `cancel` and `cancel_all` are implemented (set cancelled flag); `wait_event`, `wait_read`, `mark_read` raise `NotImplementedError`.

## Context (contract mapping)

- Requirements: User's guidance — "cancel, cancel_all — decide yourself"; "wait_event — Raise NotImplementedError (event system is out of scope)"; "wait_read, mark_read — Raise NotImplementedError (read receipts are out of scope)"
- Architecture: Single-bot-chat, single-conversation constraint

## Preconditions

- `make check` is green (baseline)
- `serverless_telegram_conversation.py` is 72 lines (plenty of room — 128 lines free)

## Non-goals

- Full event system
- Read receipt tracking
- Actually preventing method calls after cancel (cancel sets a flag but doesn't enforce it — that's future work)

## Touched surface (expected files / modules)

- `tg_auto_test/test_utils/serverless_telegram_conversation.py` (add 5 methods)
- `tests/unit/test_telethon_conformance_conversation.py` (remove 5 xfail markers)

## Dependencies and sequencing notes

- No dependencies — conversation file has plenty of room and these methods don't touch any other files.
- Fully parallelizable with all other tasks.

## Third-party / library research (mandatory for any external dependency)

- **Library**: Telethon `Conversation` class
- **Exact signatures (verified via `inspect.signature()` at runtime)**:

  **`Conversation.cancel`**:
  ```
  cancel(self)  # No parameters besides self
  ```
  Synchronous method (not async). Returns None. No parameters.

  **`Conversation.cancel_all`**:
  ```
  cancel_all(self)  # No parameters besides self
  ```
  Async method. Returns None. No parameters.

  **`Conversation.wait_event`**:
  ```
  wait_event(self, event, *, timeout=None)
  ```
  - `event`: POSITIONAL_OR_KEYWORD, no default
  - `timeout`: KEYWORD_ONLY, default=None

  **`Conversation.wait_read`**:
  ```
  wait_read(self, message=None, *, timeout=None)
  ```
  - `message`: POSITIONAL_OR_KEYWORD, default=None
  - `timeout`: KEYWORD_ONLY, default=None

  **`Conversation.mark_read`**:
  ```
  mark_read(self, message=None)
  ```
  - `message`: POSITIONAL_OR_KEYWORD, default=None

  **Important**: `cancel` is synchronous (not `async def`). `cancel_all` IS `async def` in Telethon. `wait_event` is `async def`. `wait_read` is NOT async (it's a sync method that returns a future in Telethon — but our conformance test only checks the signature, not the async-ness). `mark_read` is NOT async (it's decorated with `@_checks_cancelled` and is sync).

  **For our stubs**: The conformance tests check `inspect.signature()` parameter names only, NOT whether the method is async or sync. So we can choose async or sync. Since most methods in our codebase are async, and it doesn't affect the signature check, we'll make `wait_event`, `wait_read`, `mark_read` async (consistent with other methods raising NotImplementedError). But `cancel` MUST be sync (because Telethon's cancel is sync, and user code calls it without `await`).

## Implementation steps (developer-facing)

1. **Add `cancel` method** (synchronous — NOT async):
   ```python
   def cancel(self) -> None:
       raise NotImplementedError(
           "cancel() is not supported in serverless testing mode"
       )
   ```
   The user said we "could implement" cancel. However, implementing it meaningfully (preventing further send_message/get_response calls) would require modifying all existing methods to check a `_cancelled` flag. Since the conformance test only checks existence and signature, raise `NotImplementedError` for now.

2. **Add `cancel_all` method** (async):
   ```python
   async def cancel_all(self) -> None:
       raise NotImplementedError(
           "cancel_all() is not supported in serverless testing mode"
       )
   ```

3. **Add `wait_event` method**:
   ```python
   async def wait_event(self, event: object, *, timeout: float | None = None) -> object:
       raise NotImplementedError(
           "wait_event() requires the event system and is not supported"
       )
   ```

4. **Add `wait_read` method**:
   ```python
   def wait_read(self, message: object = None, *, timeout: float | None = None) -> object:
       raise NotImplementedError(
           "wait_read() requires read receipt tracking and is not supported"
       )
   ```

5. **Add `mark_read` method**:
   ```python
   def mark_read(self, message: object = None) -> None:
       raise NotImplementedError(
           "mark_read() requires read receipt tracking and is not supported"
       )
   ```

6. **Remove 5 xfail markers** from `tests/unit/test_telethon_conformance_conversation.py`:
   - Remove `@pytest.mark.xfail(strict=True, reason="Divergence: missing cancel method")` from `test_conversation_cancel_method`
   - Remove `@pytest.mark.xfail(strict=True, reason="Divergence: missing cancel_all method")` from `test_conversation_cancel_all_method`
   - Remove `@pytest.mark.xfail(strict=True, reason="Divergence: missing wait_event method")` from `test_conversation_wait_event_signature`
   - Remove `@pytest.mark.xfail(strict=True, reason="Divergence: missing wait_read method")` from `test_conversation_wait_read_signature`
   - Remove `@pytest.mark.xfail(strict=True, reason="Divergence: missing mark_read method")` from `test_conversation_mark_read_signature`
   - Also remove `import pytest` from the test file if it's no longer used (check: the non-xfail tests don't use pytest markers, just plain asserts. Confirm `pytest` is no longer imported anywhere in the file).

7. **Verify line count**: `serverless_telegram_conversation.py` goes from 72 to ~95 lines. Well under 200.

8. **Run `make check`** — must be 100% green.

## Production safety constraints (mandatory)

N/A — testing library, no production resources.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: simple NotImplementedError stubs, no complex logic.
- **Correct file locations**: methods added to existing `serverless_telegram_conversation.py`.
- **No regressions**: all existing tests pass; 5 tests transition from xfail to pass.

## Error handling + correctness rules (mandatory)

- All 5 methods raise `NotImplementedError` with clear error messages.
- No silent failures.

## Zero legacy tolerance rule (mandatory)

- Remove all 5 `@pytest.mark.xfail` decorators.
- Remove `import pytest` from test file if no longer needed.

## Acceptance criteria (testable)

1. `ServerlessTelegramConversation` has `cancel`, `cancel_all`, `wait_event`, `wait_read`, `mark_read` methods.
2. `cancel` signature: `(self)` — sync method, no params.
3. `cancel_all` signature: `(self)` — no params.
4. `wait_event` signature: `(self, event, *, timeout=None)` — param names `['event', 'timeout']`.
5. `wait_read` signature: `(self, message=None, *, timeout=None)` — param names `['message', 'timeout']`.
6. `mark_read` signature: `(self, message=None)` — param names `['message']`.
7. All 5 conformance tests pass (no xfail).
8. All methods raise `NotImplementedError` when called.
9. `serverless_telegram_conversation.py` under 200 lines.
10. `make check` is 100% green.

## Verification / quality gates

- [ ] `make check` passes
- [ ] 5 previously-xfail tests now pass
- [ ] `wc -l` on modified files < 200
- [ ] No new warnings introduced

## Edge cases

- `cancel` is sync in Telethon. Conformance test uses `inspect.signature()` which works the same for sync and async. But verify that `hasattr(ServerlessTelegramConversation, 'cancel')` returns True.
- `wait_read` in Telethon is sync (returns a future). Our stub is also sync. This matches.
- `mark_read` in Telethon is sync (decorated). Our stub is also sync. This matches.

## Notes / risks

- **Risk**: `cancel` being sync while most other methods are async might confuse callers.
  - **Mitigation**: This matches Telethon's actual interface — `cancel()` is explicitly documented as synchronous in Telethon. Our stub preserves this.
