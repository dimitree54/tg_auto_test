---
Task ID: `T4`
Title: `Add ~55 missing client method/property stubs`
Depends on: T2
Parallelizable: yes, with T5 and T6
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Add `NotImplementedError`-raising stubs for all ~55 missing Telethon `TelegramClient` methods and properties identified by T1's reverse conformance tests. After this task, the reverse conformance test for the client class passes (all xfail markers removed for client members).

## Context (contract mapping)

- Requirements: User's GAP 2 — ~55 missing client methods/properties
- Architecture: Stubs distributed across the mixin files created in T2, each file staying under 200 lines

## Preconditions

- T2 complete (client API decomposed into multiple mixin files with headroom)
- T1's reverse conformance test output provides the authoritative list of missing members
- `make check` is green

## Non-goals

- Implementing real behavior for any stub
- Modifying existing working methods

## Touched surface (expected files / modules)

- `tg_auto_test/test_utils/serverless_client_auth_stubs.py` (NEW — auth/connection stubs)
- `tg_auto_test/test_utils/serverless_client_admin_stubs.py` (NEW — admin/moderation stubs)
- `tg_auto_test/test_utils/serverless_client_iter_stubs.py` (NEW — iteration/download stubs)
- `tg_auto_test/test_utils/serverless_client_misc_stubs.py` (NEW — event handlers, misc stubs, properties)
- `tg_auto_test/test_utils/serverless_client_public_api.py` (MODIFY — may add some stubs here if headroom allows, OR update inheritance to chain new mixins)
- `tg_auto_test/test_utils/serverless_client_query_api.py` (MODIFY — update inheritance to chain new mixins)
- `tests/unit/test_telethon_reverse_conformance_client.py` (MODIFY — remove xfail markers for added stubs)

## Dependencies and sequencing notes

- Depends on T2 (file decomposition must be done first).
- Can run in parallel with T5 (message stubs) and T6 (conversation/button stubs) — different files.
- The exact set of stubs comes from T1's test output, not from the audit list. The developer should run T1's test with `-v` to get the definitive list.

## Third-party / library research

- **Library**: Telethon 1.42.x
- **Client reference**: https://docs.telethon.dev/en/stable/modules/client.html
- **Key pattern**: Each stub method should use `*args, **kwargs` signature to match Telethon's generic pattern, UNLESS the reverse conformance test also checks signatures (it doesn't — it only checks `hasattr`). Using `*args, **kwargs` is the safest approach for stubs.
- **Properties**: Telethon's `TelegramClient` has properties like `loop`, `disconnected`, `flood_sleep_threshold`, `parse_mode`. These should be `@property` methods that raise `NotImplementedError`.

## Implementation steps (developer-facing)

1. **Run T1's client reverse conformance test** to get the exact list of missing members:
   ```
   uv run pytest tests/unit/test_telethon_reverse_conformance_client.py -v 2>&1 | grep XFAIL
   ```

2. **Group the missing members** into logical files. Suggested grouping (adjust based on actual test output):

   **`serverless_client_auth_stubs.py`** (~60 lines):
   - `start`, `sign_in`, `sign_up`, `send_code_request`, `log_out`
   - `is_bot`, `is_connected`, `is_user_authorized`
   - `qr_login`, `edit_2fa`

   **`serverless_client_admin_stubs.py`** (~80 lines):
   - `edit_admin`, `edit_permissions`, `kick_participant`
   - `get_permissions`, `get_admin_log`, `iter_admin_log`
   - `get_participants`, `iter_participants`, `get_stats`
   - `pin_message`, `unpin_message`
   - `edit_message`, `delete_messages`, `forward_messages`
   - `send_read_acknowledge`

   **`serverless_client_iter_stubs.py`** (~70 lines):
   - `iter_dialogs`, `iter_messages`, `iter_drafts`, `iter_profile_photos`, `iter_download`
   - `download_file`, `download_profile_photo`, `upload_file`
   - `get_profile_photos`, `get_drafts`

   **`serverless_client_misc_stubs.py`** (~80 lines):
   - `action`, `add_event_handler`, `remove_event_handler`, `list_event_handlers`, `on`
   - `build_reply_markup`, `catch_up`, `delete_dialog`, `edit_folder`
   - `end_takeout`, `get_peer_id`, `inline_query`
   - `run_until_disconnected`, `set_proxy`, `set_receive_updates`, `takeout`
   - Properties: `disconnected`, `flood_sleep_threshold`, `loop`, `parse_mode`

3. **Create each mixin file** with the stubs:
   - Each stub method: `async def method_name(self, *args, **kwargs): raise NotImplementedError("method_name() is not supported in serverless testing mode")`
   - Each stub property: `@property\ndef prop_name(self): raise NotImplementedError("prop_name is not supported in serverless testing mode")`
   - For methods that are sync in Telethon (like `is_connected`, `is_bot`), use sync methods (no `async`). Check Telethon source to determine sync vs async.
   - For properties with setters in Telethon (like `parse_mode`, `flood_sleep_threshold`), add both getter and setter, both raising `NotImplementedError`.

4. **Chain the mixin inheritance**:
   - Option A: Linear chain: `ServerlessClientQueryAPI` → `ServerlessClientAuthStubs` → `ServerlessClientAdminStubs` → `ServerlessClientIterStubs` → `ServerlessClientMiscStubs`
   - Option B: All mixins as bases of `ServerlessClientPublicAPI` using multiple inheritance.
   - Choose whichever keeps files cleanest. The linear chain (Option A) is simpler and avoids MRO complexity.

5. **Update `tests/unit/test_telethon_reverse_conformance_client.py`**:
   - Remove `xfail` markers for all members that now have stubs.
   - Update the allowlist if any members were determined to be intentionally skipped.

6. **Run `make check`** — must be 100% green.

7. **Verify line counts**: Every file under 200 lines.

## Production safety constraints (mandatory)

N/A — testing library, no production resources.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: Adding stubs to the mixin architecture created in T2.
- **Correct file locations**: All new files in `tg_auto_test/test_utils/` with `serverless_client_*` naming.
- **No regressions**: Existing tests pass; xfail markers removed only for added stubs.

## Error handling + correctness rules (mandatory)

- Every stub raises `NotImplementedError` with a descriptive message.
- No silent fallbacks, no empty returns, no "pretend success."

## Zero legacy tolerance rule (mandatory)

- All xfail markers for client members must be removed from the reverse conformance test.
- No dead code in stub files.

## Acceptance criteria (testable)

1. All ~55 missing client methods/properties exist on `ServerlessTelegramClientCore` (via MRO).
2. Each stub raises `NotImplementedError` when called.
3. Reverse conformance test for client passes with no xfail markers remaining for client members.
4. Every new mixin file is under 200 lines.
5. `make check` is 100% green.

## Verification / quality gates

- [ ] `make check` passes
- [ ] `uv run pytest tests/unit/test_telethon_reverse_conformance_client.py -v` — all tests pass (no xfail)
- [ ] `wc -l` on all new client mixin files shows < 200
- [ ] No new warnings introduced

## Edge cases

- Some Telethon methods may be sync, some async. The stub must match (sync raises `NotImplementedError` synchronously, async raises it after `await`). Check Telethon source for each.
- `is_connected()` in Telethon is a method, not a property. Stub as method.
- `is_bot()` in Telethon is a method. Stub as method.
- `loop` is a property in Telethon. Stub as `@property`.
- `parse_mode` has both getter and setter. Add both.

## Notes / risks

- **Risk**: The exact number of stubs may differ from the ~55 estimate after T1 runs.
  - **Mitigation**: The developer uses T1's test output as the authoritative list. More or fewer stubs is fine — the goal is zero xfail in the client reverse conformance test.
- **Risk**: Creating 4 new files may trigger jscpd (copy-paste detection) since all stubs follow the same pattern.
  - **Mitigation**: jscpd has a minimum threshold. Each stub has a unique method name and error message, which should be sufficient differentiation. If jscpd flags it, adjust the error messages to be more descriptive per method.
