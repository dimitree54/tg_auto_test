---
Task ID: `T8`
Title: `Update vulture whitelist and run final make check validation`
Depends on: T2, T4, T5, T6, T7
Parallelizable: no (final task, depends on all others)
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Ensure `vulture_whitelist.py` includes all new public symbols (from T2-T7) so `make check` passes end-to-end. Verify all 15 xfail markers are removed, Demo UI tests pass, and all tests pass.

## Context (contract mapping)

- Requirements: `make check` must be 100% green after all tasks
- Architecture: `vulture` dead-code detection requires whitelisting public API symbols

## Preconditions

- T2, T4, T5, T6, T7 all completed
- All 15 xfail markers removed from test files
- Demo UI routes fixed (T7)

## Non-goals

- Adding any new methods or properties (that's done in earlier tasks)
- Removing existing whitelist entries

## Touched surface (expected files / modules)

- `vulture_whitelist.py` (add new public symbols)

## Dependencies and sequencing notes

- Must run after all other tasks because it validates the final state.
- Cannot run in parallel with anything.

## Third-party / library research

No third-party libraries involved. Vulture is a dead-code finder; whitelist entries are just variable/function names.

## Implementation steps (developer-facing)

1. **Run `make check`** to see if vulture reports any new unused symbols.

2. **Identify new public symbols that need whitelisting**. These are methods/properties added in T2-T7 that are part of the public API but may not be called in the library's own code:

   From T2 (client methods):
   - `send_message` — already in whitelist (line 18)
   - `send_file` — already in whitelist (line 19)
   - `download_media` — already in whitelist (line 9)
   - `get_entity` — may need addition

   From T4 (message properties):
   - `sender_id`, `chat_id`, `raw_text`, `reply_to_msg_id` — may need addition
   - `sender`, `chat`, `forward`, `via_bot` — may need addition
   - `sticker`, `contact`, `venue` — may need addition
   - `audio`, `video`, `gif`, `game`, `web_preview`, `dice` — may need addition

   From T5 (message methods):
   - `delete`, `edit`, `reply`, `forward_to`, `get_reply_message` — may need addition

   From T6 (conversation methods):
   - `cancel`, `cancel_all`, `wait_event`, `wait_read`, `mark_read` — may need addition

   From T7 (Demo UI):
   - Any new route handler names or extracted functions — check if vulture flags them

3. **Add missing entries** to `vulture_whitelist.py` under a clear comment section:
   ```python
   # Telethon interface stubs (public API for test consumers)
   get_entity
   sender_id
   chat_id
   raw_text
   reply_to_msg_id
   sender
   chat
   forward
   via_bot
   sticker
   contact
   venue
   audio
   video
   gif
   game
   web_preview
   dice
   delete
   edit
   reply
   forward_to
   get_reply_message
   cancel
   cancel_all
   wait_event
   wait_read
   mark_read
   ```

   Only add entries that vulture actually reports as unused. Do NOT blindly add all — run vulture first to see what's needed.

4. **Run `make check`** — must be 100% green:
   - `ruff format` — no changes
   - `ruff check --fix` — no issues
   - `pylint` — all files under 200 lines
   - `vulture` — no unused code (after whitelist updates)
   - `jscpd` — no code duplication
   - `pytest` — all 125 tests pass (0 xfail)

5. **Verify test count**:
   ```bash
   uv run pytest -v 2>&1 | tail -5
   ```
   Should show all tests passing with 0 xfailed. Count may be 125+ if T7 adds new tests.

6. **Verify Demo UI files** are also under 200 lines:
   ```bash
   wc -l tg_auto_test/demo_ui/server/*.py
   ```

## Production safety constraints (mandatory)

N/A — testing library, no production resources.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: only adding whitelist entries.
- **Correct file locations**: modifying existing `vulture_whitelist.py`.
- **No regressions**: final validation ensures everything passes.

## Error handling + correctness rules (mandatory)

- N/A — whitelist file has no error handling.

## Zero legacy tolerance rule (mandatory)

- No dead code remaining.
- All xfail markers removed.
- No orphaned imports in any modified file.

## Acceptance criteria (testable)

1. `make check` is 100% green.
2. `pytest` reports 0 xfailed, all tests passing.
3. `pylint` reports all files under 200 lines.
4. `vulture` reports no unused code.
5. `jscpd` reports no code duplication.
6. No file in `tg_auto_test/test_utils/` or `tg_auto_test/demo_ui/server/` exceeds 200 lines.
7. `grep -r "_pop_response" tg_auto_test/demo_ui/` returns zero matches.
8. `grep -r "InputPeerEmpty\|InputPeerUser(user_id=0" tg_auto_test/demo_ui/server/routes*.py` returns zero matches.

## Verification / quality gates

- [ ] `make check` passes end-to-end
- [ ] `uv run pytest -v` shows 125 passed, 0 xfailed
- [ ] `wc -l tg_auto_test/test_utils/*.py` — all files < 200 lines
- [ ] `wc -l tg_auto_test/demo_ui/server/*.py` — all files < 200 lines
- [ ] No `_pop_response` in Demo UI code
- [ ] No dummy `InputPeerEmpty`/`InputPeerUser(user_id=0)` in Demo UI routes

## Edge cases

- Some new properties like `voice` and `video_note` already exist in the whitelist — don't duplicate.
- `send_message` is used both as a FastAPI route handler name and as a method name — it's already whitelisted.
- `cancel` could conflict with built-in — verify vulture handles it correctly.

## Notes / risks

- **Risk**: Vulture might not flag all needed symbols if they're used internally (e.g., `raw_text` might be accessed somewhere in serialize.py via `getattr`).
  - **Mitigation**: `getattr` calls are not detected by vulture. But our new properties are on `ServerlessMessage`, and serialize.py uses `getattr(message, 'text', '')` not `message.raw_text`. So vulture will correctly flag `raw_text` as unused. Add it to whitelist.
