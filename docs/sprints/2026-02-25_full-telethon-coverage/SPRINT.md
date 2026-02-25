---
Sprint ID: `2026-02-25_full-telethon-coverage`
Sprint Goal: `Add reverse conformance tests for all 4 fake classes, stub ~86 missing Telethon methods/properties, and eliminate pop_response() from Demo UI routes`
Status: `planning`
---

## Goal

Close every remaining Telethon interface gap in our fake testing library. After this sprint: (1) auto-detecting reverse conformance tests prove that every public method on real Telethon also exists on our fakes, (2) ~86 missing methods/properties raise `NotImplementedError` instead of `AttributeError`, and (3) Demo UI routes no longer depend on the non-Telethon `pop_response()` method.

## Scope

### In
- **GAP 1 — Reverse conformance tests** for all 4 classes (`TelegramClient`, `Message`, `Conversation`, `MessageButton`) that auto-detect new Telethon public members
- **GAP 2 — ~86 missing Telethon stubs** across Client (~55), Message (~32), Conversation (~8), Button (~4), all raising `NotImplementedError`
- File decomposition of `serverless_client_public_api.py` (165 lines + ~55 stubs) and `serverless_message_properties.py` (197 lines + ~32 stubs) into multiple mixins
- Vulture whitelist updates for all new public symbols
- **GAP 3 — Demo UI `pop_response()` removal** from `routes_interactive.py` (3 call sites)

### Out
- Implementing real behavior for any stub (all raise `NotImplementedError`)
- Changing existing method implementations that already work
- Frontend JS/CSS changes
- Making Demo UI work with a live Telegram server

## Inputs (contracts)

- Requirements: User's audit finding ~86 missing public Telethon methods/attributes; three gaps to close
- Architecture: 200-line file limit (`AGENTS.md`); mixin decomposition pattern (Sprint 2); single-bot-chat constraint
- Related: Previous sprint `docs/sprints/2026-02-25_complete-telethon-stubs/`

## Change digest

- **Requirement deltas**: Previous sprint added ~25 stubs but only tested "no extra methods beyond Telethon" (forward direction). This sprint adds reverse conformance tests ("every Telethon method exists on our fakes") and closes the ~86-method gap those tests will expose.
- **Architecture deltas**: `serverless_client_public_api.py` (165 lines) and `serverless_message_properties.py` (197 lines) must be decomposed into multiple mixin files before absorbing new stubs. Conversation and Button files have headroom.

## Task list (dependency-aware)

- **T1:** `TASK_01_reverse_conformance_tests.md` (depends: —) — Add reverse conformance tests for all 4 classes (auto-detecting, with allowlists)
- **T2:** `TASK_02_decompose_client_api.md` (depends: T1) — Split `serverless_client_public_api.py` into multiple mixin files to make room for ~55 client stubs
- **T3:** `TASK_03_decompose_message_props.md` (depends: T1) (parallel: yes, with T2) — Split `serverless_message_properties.py` into multiple mixin files to make room for ~32 message stubs
- **T4:** `TASK_04_client_stubs.md` (depends: T2) — Add ~55 missing client method/property stubs across the decomposed mixin files
- **T5:** `TASK_05_message_stubs.md` (depends: T3) (parallel: yes, with T4) — Add ~32 missing message method/property stubs across the decomposed mixin files
- **T6:** `TASK_06_conversation_button_stubs.md` (depends: T1) (parallel: yes, with T2–T5) — Add ~8 conversation stubs and ~4 button stubs (files have headroom)
- **T7:** `TASK_07_demo_ui_pop_response.md` (depends: T4) — Remove `pop_response()` from `routes_interactive.py` (3 call sites)
- **T8:** `TASK_08_vulture_final_check.md` (depends: T4, T5, T6, T7) — Update vulture whitelist for all new symbols; final `make check` validation

## Dependency graph (DAG)

- T1 → T2
- T1 → T3
- T1 → T6
- T2 → T4
- T3 → T5
- T4 → T7
- T4 → T8
- T5 → T8
- T6 → T8
- T7 → T8

## Execution plan

### Critical path
T1 → T2 → T4 → T7 → T8

### Parallel tracks (lanes)

- **Lane A (Client)**: T2 → T4 → T7
- **Lane B (Message)**: T3 → T5
- **Lane C (Conversation + Button)**: T6
- **Lane D (Finalize)**: T8 (waits for T4, T5, T6, T7)
- **Foundation**: T1 (must complete before all other lanes start)

## Production safety

This is a **testing library** — there is no production database and no deployed service. All changes are to Python source code and tests.

- **Production database**: N/A — no database in this project
- **Shared resource isolation**: N/A — library code only
- **Migration deliverable**: N/A — no data model changes

## Definition of Done (DoD)

All items must be true:

- ✅ Reverse conformance tests exist for all 4 classes (Client, Message, Conversation, Button)
- ✅ Reverse conformance tests pass — every public Telethon method/attribute exists on our fakes (via `hasattr`)
- ✅ All ~86 missing stubs added, each raising `NotImplementedError`
- ✅ Demo UI `routes_interactive.py` contains zero `pop_response()` calls
- ✅ `make check` is 100% green (ruff format, ruff check, pylint 200-line limit, vulture, jscpd, pytest)
- ✅ No file exceeds 200 lines
- ✅ Zero legacy tolerance: no dead code, no orphaned imports, no duplicate helpers
- ✅ No errors are silenced (no swallowed exceptions; no "pretend success")
- ✅ Requirements/architecture docs unchanged

## Risks + mitigations

- **Risk**: The audit list of ~86 missing methods may not be 100% accurate — some may be inherited, dunder, or class-level.
  - **Mitigation**: T1's reverse conformance tests introspect real Telethon at runtime and are the authoritative source. The dev should use T1's test failures to determine the true list in T4–T6.

- **Risk**: `serverless_client_public_api.py` (165 lines) + ~55 stubs → far exceeds 200 lines. Must split into 3–4 files.
  - **Mitigation**: T2 explicitly plans decomposition into logical mixin groups (auth, messaging, admin, iteration, etc.) before any stubs are added.

- **Risk**: `serverless_message_properties.py` (197 lines) + ~32 stubs → far exceeds 200 lines. Must split into 2–3 files.
  - **Mitigation**: T3 explicitly plans decomposition into logical mixin groups (media props, metadata props, serialization stubs, etc.) before stubs are added.

- **Risk**: Removing `pop_response()` from Demo UI may break the request-response flow for invoice/poll/callback.
  - **Mitigation**: T7 replaces with conversation pattern (already used by other routes) or `_process_callback_query` direct call. Demo UI tests updated in the same task.

- **Risk**: Telethon's `Message` inherits from `ChatGetter`, `SenderGetter`, and TLObject — many "public" attributes come from these mixins and may include TL-protocol internals (e.g., `CONSTRUCTOR_ID`, `SUBCLASS_OF_ID`, `from_reader`, `serialize_bytes`).
  - **Mitigation**: Reverse conformance tests maintain an explicit allowlist of Telethon-internal attributes that we intentionally skip, with documented reasons. The allowlist is reviewed and kept minimal.

- **Risk**: New mixin files may trigger circular imports.
  - **Mitigation**: Mixin files import only from `models.py` and lower-level helpers, never from the core client. Core client imports mixins. This pattern is established and proven in Sprint 2.

## Migration plan (if data model changes)

N/A — no data model changes.

## Rollback / recovery notes

- Revert the commits for this sprint. All changes are additive (new stubs, new tests, new mixin files) with no behavior changes to existing methods (except `pop_response()` removal from Demo UI routes).

## Task validation status

- T1: self-validated → task-checker reviewed → approved
- T2: self-validated → task-checker reviewed → approved
- T3: self-validated → task-checker reviewed → approved
- T4: self-validated → task-checker reviewed → approved
- T5: self-validated → task-checker reviewed → approved
- T6: self-validated → task-checker reviewed → approved
- T7: self-validated → task-checker reviewed → approved
- T8: self-validated → task-checker reviewed → approved

## Sources used

- Requirements: User's sprint planning prompt (audit of ~86 missing methods)
- Architecture: `AGENTS.md` (200-line limit, decomposition policy)
- Code read (for scoping only):
  - `tg_auto_test/test_utils/serverless_client_public_api.py` (165 lines)
  - `tg_auto_test/test_utils/serverless_message_properties.py` (197 lines)
  - `tg_auto_test/test_utils/serverless_message.py` (128 lines)
  - `tg_auto_test/test_utils/serverless_telegram_conversation.py` (90 lines)
  - `tg_auto_test/test_utils/serverless_button.py` (16 lines)
  - `tg_auto_test/test_utils/serverless_telegram_client_core.py` (196 lines)
  - `tg_auto_test/test_utils/serverless_telegram_client.py` (39 lines)
  - `tg_auto_test/test_utils/models.py` (38 lines)
  - `tg_auto_test/demo_ui/server/routes_interactive.py` (70 lines)
  - `tg_auto_test/demo_ui/server/demo_server.py` (150 lines)
  - `tests/unit/test_telethon_conformance_client_basic.py` (156 lines)
  - `tests/unit/test_telethon_conformance_client_extended.py` (80 lines)
  - `tests/unit/test_telethon_conformance_message_basic.py` (106 lines)
  - `tests/unit/test_telethon_conformance_message_extended.py` (118 lines)
  - `tests/unit/test_telethon_conformance_conversation.py` (130 lines)
  - `vulture_whitelist.py` (68 lines)
  - `Makefile` (15 lines)
  - `docs/sprints/2026-02-25_complete-telethon-stubs/SPRINT.md` (213 lines)

## Contract summary

### What (requirements)
- Every public method/attribute on real Telethon classes must exist on our fake classes
- Missing items must raise `NotImplementedError` (not `AttributeError`)
- Auto-detecting reverse conformance tests must catch future Telethon additions
- Demo UI must not depend on non-Telethon `pop_response()` method

### How (architecture)
- Reverse conformance tests introspect real Telethon via `dir()` / `inspect`, assert `hasattr` on fakes, maintain explicit allowlists
- File decomposition via mixin pattern (established in Sprint 2) to stay under 200-line limit
- New mixin files: `serverless_client_auth_stubs.py`, `serverless_client_admin_stubs.py`, `serverless_client_iter_stubs.py`, `serverless_message_metadata_stubs.py`, `serverless_message_serial_stubs.py` (exact names TBD by developer based on logical grouping)
- Demo UI routes rewritten to use conversation pattern or direct `_process_callback_query` instead of `pop_response()`

## Impact inventory (implementation-facing)

- **Flows**: No existing flows change behavior; new stubs all raise `NotImplementedError`; Demo UI invoice/poll/callback routes change internal implementation but external API unchanged
- **Modules / interfaces**: 4–6 new mixin files, 4 new test files (or additions to existing conformance tests), ~5 modified source files, 1 modified vulture whitelist
- **Data model / migrations**: None
- **Security / privacy**: None
- **Performance / quality**: No performance impact; all new methods are trivial `NotImplementedError` raisers

## Decisions (made from docs; not invented)

- D1: Reverse conformance tests use `dir()` to get public members and `hasattr()` to check fakes, with an explicit allowlist for intentionally skipped items (Source: user's requirements — "auto-detecting, with allowlists")
- D2: All stubs raise `NotImplementedError` with descriptive messages (Source: user's requirement — "raise NotImplementedError instead of AttributeError")
- D3: Stub properties use `@property` decorator that raises `NotImplementedError` in the getter (Source: user's requirement — "Stub properties should also raise NotImplementedError")
- D4: File decomposition happens BEFORE stub addition (Source: user's explicit note — "Plan file decomposition tasks BEFORE stub addition tasks")
- D5: The exact list of missing methods comes from T1's reverse conformance test, not the audit (Source: user's note — "the reverse conformance test will be the authoritative source")

## Non-goals

- NG1: Implementing real behavior for any stub (Source: user's requirement — all stubs raise `NotImplementedError`)
- NG2: Frontend visual changes (Source: sprint scope — no UI requirement)
- NG3: Full event system, read receipts, entity resolution, multi-chat support (Source: established scope from Sprint 2)
