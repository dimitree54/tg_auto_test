---
Task ID: `T2`
Title: `Split serverless_client_public_api.py into multiple mixin files for client stubs`
Depends on: T1
Parallelizable: yes, with T3 and T6
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Decompose `serverless_client_public_api.py` (currently 165 lines) into multiple logical mixin files so that T4 can add ~55 client stubs without exceeding the 200-line limit in any file.

## Context (contract mapping)

- Requirements: User identified ~55 missing client methods; current file at 165 lines cannot absorb them
- Architecture: `AGENTS.md` mandates 200-line limit with logical decomposition (never compact)

## Preconditions

- T1 complete (reverse conformance tests exist and identify exact missing members)
- `make check` is green

## Non-goals

- Adding new stubs (that's T4)
- Changing behavior of existing methods

## Touched surface (expected files / modules)

- `tg_auto_test/test_utils/serverless_client_public_api.py` (MODIFY — keep core methods, reduce to ~80 lines)
- `tg_auto_test/test_utils/serverless_client_query_api.py` (NEW — extract `get_me`, `get_dialogs`, `get_messages`)
- `tg_auto_test/test_utils/serverless_telegram_client_core.py` (MODIFY — update MRO inheritance chain)

## Dependencies and sequencing notes

- Depends on T1 so the developer knows the exact list of missing client members and can plan the decomposition grouping accordingly.
- Can run in parallel with T3 (message decomposition) and T6 (conversation/button stubs) since they touch different files.

## Third-party / library research

No third-party libraries involved. This is internal refactoring using the mixin pattern established in Sprint 2.

## Implementation steps (developer-facing)

1. **Analyze T1's output** to confirm the exact list of ~55 missing client methods. Group them into logical categories:
   - **Query methods** (already exist): `get_me`, `get_dialogs`, `get_messages` — these can stay in `serverless_client_public_api.py` or move to a query mixin
   - **Messaging** (exist): `send_message`, `download_media` — in `serverless_client_public_api.py`
   - **Auth/connection**: `start`, `sign_in`, `sign_up`, `send_code_request`, `log_out`, `is_bot`, `is_connected`, `is_user_authorized`, `qr_login`, `edit_2fa`
   - **Admin/moderation**: `edit_admin`, `edit_permissions`, `kick_participant`, `get_permissions`, `get_admin_log`, `iter_admin_log`, `get_participants`, `iter_participants`, `get_stats`, `pin_message`, `unpin_message`
   - **Messaging stubs**: `edit_message`, `delete_messages`, `forward_messages`, `send_read_acknowledge`
   - **Iteration**: `iter_dialogs`, `iter_messages`, `iter_drafts`, `iter_profile_photos`, `iter_download`
   - **File/media**: `download_file`, `download_profile_photo`, `upload_file`, `get_profile_photos`
   - **Misc**: `action`, `add_event_handler`, `remove_event_handler`, `list_event_handlers`, `on`, `build_reply_markup`, `catch_up`, `delete_dialog`, `edit_folder`, `end_takeout`, `get_drafts`, `get_peer_id`, `inline_query`, `run_until_disconnected`, `set_proxy`, `set_receive_updates`, `takeout`
   - **Properties**: `disconnected`, `flood_sleep_threshold`, `loop`, `parse_mode`

2. **Create `tg_auto_test/test_utils/serverless_client_query_api.py`** (NEW):
   - Define class `ServerlessClientQueryAPI` (mixin, no base class).
   - Move `get_me`, `get_dialogs`, `get_messages` from `serverless_client_public_api.py`.
   - Add necessary imports (only what these methods need).
   - Target: ~80 lines.

3. **Update `serverless_client_public_api.py`**:
   - Inherit from `ServerlessClientQueryAPI`: `class ServerlessClientPublicAPI(ServerlessClientQueryAPI):`
   - Remove the 3 extracted methods (`get_me`, `get_dialogs`, `get_messages`).
   - Keep `conversation`, `send_message`, `download_media` (the methods that have real implementations).
   - Remove now-unused imports.
   - Target: ~90 lines — leaving ~110 lines of headroom for T4's stubs (though T4 will need additional mixin files for the ~55 stubs).

4. **Update `serverless_telegram_client_core.py`**:
   - No MRO change needed if `ServerlessClientPublicAPI` already inherits from `ServerlessClientQueryAPI`. The chain is: `ServerlessTelegramClientCore` → `ServerlessClientPublicAPI` → `ServerlessClientQueryAPI`.
   - Verify that all `self._*` references resolve correctly via MRO.

5. **Run `make check`** — must be 100% green. All existing tests pass unchanged since this is pure refactoring.

6. **Verify line counts**: All files under 200 lines, with sufficient headroom for T4.

## Production safety constraints (mandatory)

N/A — testing library, no production resources.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: Extracting existing code into a new mixin, not writing new code.
- **Correct file locations**: New file in `tg_auto_test/test_utils/` following established `serverless_client_*.py` naming.
- **No regressions**: All existing tests pass unchanged; `make check` green.

## Error handling + correctness rules (mandatory)

- No error handling changes — methods are moved verbatim.
- Do not add any try/catch or fallback behavior.

## Zero legacy tolerance rule (mandatory)

- After extraction, `serverless_client_public_api.py` must not contain the moved methods.
- Remove any imports that are no longer used after extraction.
- No duplicate code between files.

## Acceptance criteria (testable)

1. `serverless_client_query_api.py` exists with `get_me`, `get_dialogs`, `get_messages` having identical signatures and behavior.
2. `serverless_client_public_api.py` inherits from `ServerlessClientQueryAPI` and no longer contains the 3 extracted methods.
3. MRO chain is correct: `ServerlessTelegramClientCore` → `ServerlessClientPublicAPI` → `ServerlessClientQueryAPI`.
4. All files are under 200 lines.
5. `serverless_client_public_api.py` has at least ~100 lines of headroom (under ~100 lines).
6. `make check` is 100% green.

## Verification / quality gates

- [ ] `make check` passes
- [ ] `wc -l` on all client files shows < 200
- [ ] `serverless_client_public_api.py` is under 100 lines (headroom for T4)
- [ ] No new warnings introduced
- [ ] Existing conformance tests still pass

## Edge cases

- `get_messages` references `self._handle_click` and `ServerlessMessage` — confirm imports are correct in the new file and MRO resolves `self._handle_click` at runtime.
- `get_me` references `self._user_id` and `self._first_name` — these are on `ServerlessTelegramClientCore`, available via MRO.
- `get_dialogs` uses no `self._*` references — clean extraction.

## Notes / risks

- **Risk**: Circular import between new mixin and `serverless_telegram_conversation.py`.
  - **Mitigation**: `ServerlessClientQueryAPI` does not import from conversation. The `conversation()` method stays in `ServerlessClientPublicAPI` which already imports from conversation.
