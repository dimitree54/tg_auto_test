---
Task ID: `T1`
Title: `Extract client public-API surface into a mixin to free space in client_core.py`
Depends on: —
Parallelizable: yes, with T3 and T6
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Create `serverless_client_public_api.py` containing a `ServerlessClientPublicAPI` mixin class. Move `get_me`, `get_dialogs`, `get_messages`, and `conversation` from `ServerlessTelegramClientCore` into this mixin. This frees ~80 lines in `client_core.py` for T2 to add `send_message`, `send_file`, `download_media`, `get_entity`.

## Context (contract mapping)

- Requirements: User's requirement to add 4 new client methods; current file is at 200-line hard limit
- Architecture: `AGENTS.md` mandates files stay under 200 lines; decompose rather than compact

## Preconditions

- `make check` is green (baseline confirmed)
- `serverless_telegram_client_core.py` is exactly 200 lines

## Non-goals

- Adding new methods (that's T2)
- Changing any behavior of existing methods

## Touched surface (expected files / modules)

- `tg_auto_test/test_utils/serverless_client_public_api.py` (NEW — ~80 lines)
- `tg_auto_test/test_utils/serverless_telegram_client_core.py` (modify — remove extracted methods, add mixin inheritance)
- `vulture_whitelist.py` (may need temporary additions — but defer to T7 if vulture still passes)

## Dependencies and sequencing notes

- No dependencies; this is pure refactoring with no behavior change.
- Can run in parallel with T3 (message decomposition) and T6 (conversation stubs) since they touch different files.

## Third-party / library research

No third-party libraries involved. This is internal refactoring only.

## Implementation steps (developer-facing)

1. **Create `tg_auto_test/test_utils/serverless_client_public_api.py`**:
   - Define a class `ServerlessClientPublicAPI` (no base class; it's a mixin).
   - Move these methods from `ServerlessTelegramClientCore`:
     - `get_me(self, input_peer: bool = False) -> User`
     - `get_dialogs(self, limit, *, offset_date, offset_id, offset_peer, ignore_pinned, ignore_migrated, folder, archived) -> list[object]`
     - `get_messages(self, entity, limit, *, offset_date, offset_id, max_id, min_id, add_offset, search, filter, from_user, wait_time, ids, reverse, reply_to, scheduled) -> Union[ServerlessMessage, list[ServerlessMessage], None]`
     - `conversation(self, entity, *, timeout, total_timeout, max_messages, exclusive, replies_are_responses) -> ServerlessTelegramConversation`
   - Add the necessary imports at the top (only what these methods need): `Union` from typing, `User` from telethon, `ServerlessMessage` from models, `ServerlessTelegramConversation`.
   - The mixin methods will reference `self._user_id`, `self._first_name`, `self._handle_click`, `self._chat_id` — these are defined on `ServerlessTelegramClientCore` and will be available at runtime via MRO. Use `TYPE_CHECKING` and a protocol or forward reference if needed for type safety, or simply rely on duck typing (the mixin pattern is established in this codebase).

2. **Modify `serverless_telegram_client_core.py`**:
   - Add import: `from tg_auto_test.test_utils.serverless_client_public_api import ServerlessClientPublicAPI`
   - Change class declaration: `class ServerlessTelegramClientCore(ServerlessClientPublicAPI):`
   - Remove the 4 method bodies that were moved to the mixin.
   - Remove any imports that are now only used in the mixin file (e.g., `Union` from typing, `User` from telethon).
   - Keep all other methods (`__init__`, `connect`, `disconnect`, `_get_bot_state`, `_pop_response`, `_process_text_message`, `_process_file_message`, `_process_callback_query`, `_handle_send_vote_request`, `_process_message_update`, `_handle_click`, `_simulate_stars_payment`, `_api_calls`, `_last_api_call`).

3. **Verify line counts**:
   - `serverless_client_public_api.py`: should be ~70–80 lines
   - `serverless_telegram_client_core.py`: should drop from 200 to ~130 lines (freeing ~70 lines for T2)

4. **Run `make check`** — must be 100% green. All existing tests must pass unchanged since this is pure refactoring.

## Production safety constraints (mandatory)

N/A — testing library, no production resources.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: extracting existing code, not writing new code.
- **Correct file locations**: new file in `tg_auto_test/test_utils/` following existing naming convention (`serverless_*.py`).
- **No regressions**: all existing tests pass unchanged; `make check` green.

## Error handling + correctness rules (mandatory)

- No error handling changes — methods are moved verbatim.
- Do not add any try/catch or fallback behavior.

## Zero legacy tolerance rule (mandatory)

- After extraction, `serverless_telegram_client_core.py` must not contain the moved methods.
- Remove any imports from `serverless_telegram_client_core.py` that are no longer used after extraction.
- No duplicate code between the two files.

## Acceptance criteria (testable)

1. `serverless_client_public_api.py` exists and contains `get_me`, `get_dialogs`, `get_messages`, `conversation` methods with identical signatures and behavior.
2. `ServerlessTelegramClientCore` inherits from `ServerlessClientPublicAPI`.
3. `serverless_telegram_client_core.py` no longer contains `get_me`, `get_dialogs`, `get_messages`, `conversation` method bodies.
4. Both files are under 200 lines.
5. `make check` is 100% green (all 110 tests pass, 15 xfail unchanged).

## Verification / quality gates

- [ ] `make check` passes (ruff format, ruff check, pylint 200-line limit, vulture, jscpd, pytest)
- [ ] `wc -l` on both files shows < 200
- [ ] No new warnings introduced

## Edge cases

- `get_messages` references `self._handle_click` — confirm MRO resolves it correctly at runtime (it will, since `ServerlessTelegramClientCore` defines `_handle_click` and inherits from the mixin).
- `conversation` returns `ServerlessTelegramConversation(client=self)` — `self` is the concrete `ServerlessTelegramClientCore` instance, which still works.

## Notes / risks

- **Risk**: Circular import if mixin imports from `serverless_telegram_client_core.py`.
  - **Mitigation**: Mixin does NOT import from client_core. It imports from `models.py` and `serverless_telegram_conversation.py` only. Client_core imports from the mixin, not vice versa.
