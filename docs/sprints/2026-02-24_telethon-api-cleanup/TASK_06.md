# TASK_06 — Final cleanup: vulture whitelist, README, verification

**Dependencies:** TASK_01, TASK_02, TASK_03, TASK_04, TASK_05 (all previous tasks)

## Objective

Final sweep to ensure all non-Telethon public methods have been removed/privatized, the vulture whitelist is clean, README is accurate, and `make check` is fully green.

## Files to modify

| File | Change |
|------|--------|
| `vulture_whitelist.py` | Verify `click_inline_button` and `clear_bot_state` are already removed (TASK_04, TASK_05). Remove any other stale entries that reference removed methods. Ensure no new dead-code entries are needed for renamed private methods. |
| `README.md` | Verify `click_inline_button` reference was removed in TASK_05. Audit remaining API docs: confirm `api_calls` and `last_api_call` are documented as extensions. Remove any references to `process_text_message`, `process_file_message`, `process_callback_query`, `pop_response`, `simulate_stars_payment`, `get_bot_state`, or `clear_bot_state` as public API. |
| Any file with stale references | Final grep for all 8 removed/privatized method names to catch any missed references. |

## Requirements

1. Run a comprehensive grep for all original public method names across the entire codebase:
   - `process_text_message` (should only appear as `_process_text_message`)
   - `process_file_message` (should only appear as `_process_file_message`)
   - `process_callback_query` (should only appear as `_process_callback_query`)
   - `pop_response` (should only appear as `_pop_response`)
   - `simulate_stars_payment` (should only appear as `_simulate_stars_payment`)
   - `get_bot_state` (should only appear as `_get_bot_state`)
   - `clear_bot_state` (should only appear as `_clear_bot_state`)
   - `click_inline_button` (should not appear anywhere)
2. Verify that `api_calls` and `last_api_call` remain as public properties.
3. Verify vulture whitelist has no stale entries and no missing entries.
4. `make check` passes with zero warnings and zero failures.

## Verification checklist

- [ ] `grep -rn 'def process_text_message' tg_auto_test/` returns zero results
- [ ] `grep -rn 'def process_file_message' tg_auto_test/` returns zero results
- [ ] `grep -rn 'def process_callback_query' tg_auto_test/` returns zero results
- [ ] `grep -rn 'def pop_response' tg_auto_test/` returns zero results
- [ ] `grep -rn 'def simulate_stars_payment' tg_auto_test/` returns zero results
- [ ] `grep -rn 'def get_bot_state' tg_auto_test/` returns zero results
- [ ] `grep -rn 'def clear_bot_state' tg_auto_test/` returns zero results
- [ ] `grep -rn 'def click_inline_button' tg_auto_test/` returns zero results
- [ ] `grep -rn 'click_inline_button' tg_auto_test/` returns zero results
- [ ] `api_calls` property exists on `ServerlessTelegramClientCore`
- [ ] `last_api_call` property exists on `ServerlessTelegramClientCore`
- [ ] `make check` exits 0
- [ ] No file exceeds 200 lines

## Acceptance Criteria

1. All verification checks pass.
2. `make check` passes.
3. The only non-Telethon public methods/properties on the client classes are `api_calls` and `last_api_call`.
4. README accurately documents the current public API.
5. Vulture whitelist contains no references to removed methods.

## Risks

- **Missed references**: A thorough grep is essential. Check `.py` files, `.md` files, and any config files.
- **Vulture false positives**: Private methods that are only called dynamically (e.g., via Protocols) may trigger vulture. Add whitelist entries only if needed.
