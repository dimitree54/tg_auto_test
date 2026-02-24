---
Sprint ID: `2026-02-24_telethon-interface-alignment`
Sprint Goal: `Align all public interfaces of ServerlessTelegramClient, ServerlessMessage, ServerlessTelegramConversation, and Demo UI protocols to match real Telethon exactly.`
Status: `planning`
Owners: `Developer`
---

## Goal

Align every public method and property on our fake Telethon classes (`ServerlessTelegramClient`, `ServerlessMessage`, `ServerlessTelegramConversation`, `ServerlessButton`) to exactly match real Telethon 1.42 signatures. Privatize all non-Telethon public attributes, eliminate `TelethonCompatibleMessage`, and refactor the Demo UI to work through standard Telethon interfaces only.

## Scope

### In
- Fix all 23 documented interface divergences between our classes and real Telethon
- Privatize all non-Telethon public attributes on client and message classes
- Eliminate `TelethonCompatibleMessage` class entirely
- Add conformance tests that verify our interfaces match Telethon's
- Refactor Demo UI protocols/serialization to use standard Telethon interfaces
- Update README.md and CONTRIBUTING.md to document the Telethon interface contract

### Out
- Adding new features beyond interface alignment (no new Bot API methods)
- Implementing full Telethon behavior for stub methods (NotImplementedError is acceptable)
- Multi-user or multi-chat support
- Any Telethon methods not in the current scope of our client (auth, chats, etc.)
- Performance optimizations

## Inputs (contracts)

- Requirements: User-provided divergence list (23 items) in sprint request
- Architecture: Current codebase at `tg_auto_test/` (read for scoping)
- Telethon reference: [Telethon 1.42.0 docs](https://docs.telethon.dev/en/stable/)

## Change digest

- **Requirement deltas**:
  - All public interfaces must match Telethon 1.42 exactly (parameter names, kinds, defaults, types, return types)
  - Extra `_`-prefixed methods are allowed for test infrastructure
  - Unimplemented features must raise `NotImplementedError`
  - Demo UI must work with both `ServerlessTelegramClient` and real `TelegramClient`
- **Architecture deltas**:
  - `TelethonCompatibleMessage` to be eliminated; `get_messages()` returns `ServerlessMessage`
  - Six public dataclass fields on `ServerlessMessage` to be privatized
  - Five public attributes on `ServerlessTelegramClientCore` to be privatized
  - Demo UI protocols to drop `_pop_response()` and `ServerlessMessage` type coupling

## Task list (dependency-aware)

- **T1:** `TASK_01_docs_telethon_contract.md` (depends: --) (parallel: yes, with T2) -- Document Telethon interface contract in README/CONTRIBUTING
- **T2:** `TASK_02_conformance_tests.md` (depends: --) (parallel: yes, with T1) -- Create interface conformance tests
- **T3:** `TASK_03_fix_client_interface.md` (depends: T2) (parallel: no) -- Fix ServerlessTelegramClient public interface
- **T4:** `TASK_04_fix_message_interface.md` (depends: T2) (parallel: no) -- Fix ServerlessMessage/ServerlessButton public interface and eliminate TelethonCompatibleMessage
- **T5:** `TASK_05_fix_conversation_interface.md` (depends: T2) (parallel: no) -- Fix ServerlessTelegramConversation public interface
- **T6:** `TASK_06_demo_ui_universal_protocol.md` (depends: T3, T4, T5) (parallel: no) -- Refactor Demo UI to use standard Telethon interfaces

## Dependency graph (DAG)

- T1 (independent)
- T2 (independent)
- T2 -> T3
- T2 -> T4
- T2 -> T5
- T3 -> T6
- T4 -> T6
- T5 -> T6

## Execution plan

### Critical path
- T2 -> T3 -> T6
- T2 -> T4 -> T6
- T2 -> T5 -> T6

### Parallel tracks (lanes)

- **Lane A (docs)**: T1 (fully independent, can run anytime)
- **Lane B (core alignment)**: T2 -> T3 -> T4 -> T5 -> T6 (serialized to avoid merge conflicts on shared files: models.py, client_core.py, tests)

Note: While T3, T4, T5 are theoretically parallelizable, they share heavy overlap on `models.py`, test files, and `vulture_whitelist.py`. Serializing them within Lane B is safer and avoids merge conflicts.

## Production safety

- **Production database**: N/A -- this is a testing library with no database.
- **Shared resource isolation**: N/A -- no production instance; this is a library, not a deployed service.
- **Migration deliverable**: N/A -- no data model changes.

## Definition of Done (DoD)

All items must be true:

- All tasks completed and verified
- `make check` passes 100% (ruff, pylint, vulture, jscpd, pytest)
- All 18+ existing tests continue to pass
- New conformance tests pass (our interfaces match Telethon's)
- Zero legacy tolerance (TelethonCompatibleMessage removed; no dead code; no parallel old/new paths)
- No errors are silenced (no swallowed exceptions; no "pretend success")
- No new "temporary" toggles/workarounds
- README.md and CONTRIBUTING.md updated with Telethon interface contract
- Demo UI works with both ServerlessTelegramClient and real TelegramClient (via protocols)
- All files <= 200 lines (decompose if needed)

## Risks + mitigations

- **Risk**: Privatizing public attributes breaks existing consumer code
  - **Mitigation**: This is a library; consumers must update. The conformance tests ensure we match Telethon. Version bump communicates breaking change.

- **Risk**: File size limit (200 lines) hit when adding NotImplementedError stubs to ServerlessMessage
  - **Mitigation**: Plan file decomposition explicitly in T4. Extract property stubs into a mixin or separate module.

- **Risk**: Demo UI `serialize.py` and `routes.py` tightly coupled to `ServerlessMessage` internals
  - **Mitigation**: T6 explicitly refactors serialization to use Telethon-standard properties only.

- **Risk**: T3/T4/T5 touch overlapping files (models.py, vulture_whitelist.py, tests)
  - **Mitigation**: Serialize these tasks (Lane B) to avoid merge conflicts.

## Migration plan (if data model changes)

N/A -- no data model changes.

## Rollback / recovery notes

- All changes are code-only (no database, no deployment). Rollback is a git revert.

## Task validation status

- T1: pending
- T2: pending
- T3: pending
- T4: pending
- T5: pending
- T6: pending

## Sources used

- Requirements: User-provided divergence list (23 items)
- Architecture: N/A (no docs/architecture/ directory)
- Code read (for scoping): `tg_auto_test/test_utils/serverless_telegram_client.py`, `serverless_telegram_client_core.py`, `serverless_telegram_conversation.py`, `models.py`, `telethon_compatible_message.py`, `demo_ui/server/demo_server.py`, `demo_ui/server/routes.py`, `demo_ui/server/serialize.py`, `demo_ui/server/upload_handlers.py`, `README.md`, `CONTRIBUTING.md`, `Makefile`, `pyproject.toml`, `vulture_whitelist.py`, all test files in `tests/unit/`
- Telethon docs: https://docs.telethon.dev/en/stable/modules/client.html, https://docs.telethon.dev/en/stable/modules/custom.html, https://docs.telethon.dev/en/stable/quick-references/client-reference.html

## Contract summary

### What (requirements)
- All public interfaces on fake classes must match real Telethon 1.42 signatures exactly
- Extra `_`-prefixed methods are allowed for test infrastructure
- Unimplemented features raise `NotImplementedError`
- Demo UI must work with both fake and real clients

### How (architecture)
- Privatize non-Telethon public attributes (`request`, `application`, `chat_id`, `user_id`, `first_name`, `poll_data`, `response_file_id`, `reply_markup_data`, `media_photo`, `media_document`, `invoice_data`)
- Eliminate `TelethonCompatibleMessage`; return `ServerlessMessage` from `get_messages()`
- Fix method signatures (param names, keyword-only markers, defaults, types)
- Add `NotImplementedError` stubs for unsupported Telethon features
- Refactor Demo UI protocols to use only Telethon-standard interfaces

## Impact inventory (implementation-facing)

- **Flows**: conversation creation, message sending/receiving, button clicking, file upload, poll voting, stars payment, demo UI interactions
- **Modules / interfaces**: `serverless_telegram_client.py`, `serverless_telegram_client_core.py`, `serverless_telegram_conversation.py`, `models.py`, `telethon_compatible_message.py` (deleted), `demo_server.py`, `routes.py`, `serialize.py`, `upload_handlers.py`, `vulture_whitelist.py`, all test files
- **Data model / migrations**: None
- **Security / privacy**: None
- **Performance / quality**: None (interface changes only)

## Decisions (made from docs; not invented)

- D1: Serialize T3/T4/T5 to avoid merge conflicts on shared files (Source: codebase analysis -- models.py, tests, vulture_whitelist.py all shared)
- D2: Use `NotImplementedError` for unsupported Telethon features rather than silent no-ops (Source: user requirement "fail-fast design")
- D3: Keep `_api_calls` and `_last_api_call` as `_`-prefixed (already private) (Source: codebase -- they're already prefixed)

## Non-goals

- NG1: Implementing full Telethon behavior for stub methods (NotImplementedError is the contract)
- NG2: Adding new Bot API method support beyond what exists today
- NG3: Multi-user/multi-chat support
- NG4: Changing the internal PTB bridge architecture
