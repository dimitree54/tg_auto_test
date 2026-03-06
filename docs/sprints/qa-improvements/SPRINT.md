---
Sprint ID: `2026-03-06_qa-improvements`
Sprint Goal: `Add return-type conformance, behavioral parity, and NotImplementedError classification tests`
Sprint Type: `module`
Module: `tests/unit (QA test infrastructure)`
Status: `planning`
---

## Goal

Strengthen the QA safety net for the fake-Telethon library by closing three blind spots:
return-type annotations are not verified, behavioral contracts are not tested, and
`NotImplementedError` stubs have no tracked classification. These three test suites will
prevent regressions like issue #25 (`click()` returning wrong type) and issue #24
(`get_edit()` left as unimplemented stub) from reaching consumers.

## Module Scope

### What this sprint implements

- Three new conformance / integration test files in `tests/unit/`
- No production source changes

### Boundary Rules (STRICTLY ENFORCED)

**ALLOWED - this sprint may ONLY touch:**
- `tests/unit/` - new test files only
- `vulture_whitelist.py` - if new test helpers trigger vulture false positives
- `docs/sprints/qa-improvements/` - sprint planning files

**FORBIDDEN - this sprint must NEVER touch:**
- `tg_auto_test/` source code
- Existing test files in `tests/unit/`
- Linter configuration (`ruff.toml`, `pyproject.toml`, `Makefile`)
- Any docs outside `docs/sprints/qa-improvements/`

### Test Scope

- **Test directory**: `tests/unit/`
- **Test command**: `uv run pytest tests/unit/<new_test_file>.py -x -v`
- **Full validation**: `make check`

## Scope

### In

- T1: Return-type annotation conformance tests for all methods with concrete Telethon signatures
- T2: Behavioral parity integration tests for core conversation patterns
- T3: NotImplementedError stub classification and tracking test

### Out

- Fixing any return-type mismatches found (separate work)
- Implementing any stubs classified as IMPLEMENTABLE (separate work)
- Changes to source code under `tg_auto_test/`

## Inputs (contracts)

- Requirements: `CONTRIBUTING.md` (conformance test policy, design philosophy)
- Architecture: Codebase structure in `tg_auto_test/test_utils/`
- Existing conformance tests: `tests/unit/test_telethon_conformance_*.py`, `tests/unit/test_telethon_reverse_conformance_*.py`
- Bug reproduction tests: `tests/unit/test_click_returns_message_bug.py`, `tests/unit/test_get_edit_bug.py`

## Change digest

- **Requirement deltas**: None - this sprint adds tests to enforce existing policy
- **Architecture deltas**: None - no source code changes

## Task list (dependency-aware)

- **T1:** `TASK_return_type_conformance.md` (depends: --) (parallel: yes, with T3) - Return-type annotation conformance tests
- **T2:** `TASK_behavioral_parity.md` (depends: --) (parallel: yes, with T1, T3) - Behavioral parity integration tests
- **T3:** `TASK_stub_classification.md` (depends: --) (parallel: yes, with T1, T2) - NotImplementedError stub classification tests

## Dependency graph (DAG)

All three tasks are independent. No inter-task dependencies.

```
T1 (return types)     -- independent
T2 (behavioral)       -- independent
T3 (stub tracking)    -- independent
```

## Execution plan

### Critical path

No dependencies - all tasks are on the critical path equally.

### Parallel tracks (lanes)

- **Lane A**: T1
- **Lane B**: T2
- **Lane C**: T3

All three lanes can execute simultaneously.

## Production safety

N/A - this sprint creates only test files. No database, no shared resources, no runtime changes.

- **Production database**: N/A
- **Shared resource isolation**: N/A - tests run in-memory with no external dependencies
- **Migration deliverable**: N/A

## Definition of Done (DoD)

All items must be true:

- All tasks completed and verified
- New tests pass: `uv run pytest tests/unit/<new_file>.py -x -v` for each new file
- `make check` passes 100% (ruff, pylint 200-line limit, vulture, jscpd, pytest)
- No existing test files modified
- No source code under `tg_auto_test/` modified
- Each new test file stays under 200 lines (decompose if needed)
- Zero legacy tolerance (no dead code, no commented-out code)
- No errors silenced

## Risks + mitigations

- **Risk**: Telethon uses `(*args, **kwargs)` on many methods, making `inspect.get_annotations` return `inspect.Parameter.empty` for return types. Tests that blindly check all methods will produce false negatives.
  - **Mitigation**: T1 explicitly enumerates methods with concrete Telethon signatures and skips `(*args, **kwargs)` wrappers.

- **Risk**: New test files exceed the 200-line limit.
  - **Mitigation**: Each task specifies decomposition strategy (helper modules, parametrized tests).

- **Risk**: `inspect.get_annotations` behaves differently for properties vs methods vs classmethods.
  - **Mitigation**: T1 task instructions specify using `typing.get_type_hints()` with fallback to `inspect.signature().return_annotation`.

- **Risk**: Behavioral tests (T2) depend on specific PTB handler wiring, which may be fragile.
  - **Mitigation**: T2 defines self-contained handler functions within the test file, not importing from other test files.

- **Risk**: Stub classification (T3) becomes stale as new stubs are added.
  - **Mitigation**: T3 includes a self-updating scan that fails when unclassified stubs are found.

## Rollback / recovery notes

- Delete the new test files. No source code was changed, so no rollback is needed.

## Task validation status

- Per-task validation order: `T1` -> `T2` -> `T3`
- Validator: self-validated against checklists
- Outcome: approved
- Notes: All three tasks are independent, test-only additions

## Sources used

- CONTRIBUTING.md (design philosophy, conformance test policy)
- `tg_auto_test/test_utils/serverless_message.py` (ServerlessMessage class, stubs)
- `tg_auto_test/test_utils/serverless_telegram_conversation.py` (conversation stubs)
- `tg_auto_test/test_utils/serverless_telegram_client_core.py` (client core)
- `tg_auto_test/test_utils/serverless_client_public_api.py` (conversation, send_message, download_media)
- `tg_auto_test/test_utils/serverless_client_query_api.py` (get_me, get_messages, get_dialogs)
- `tg_auto_test/test_utils/serverless_client_misc_stubs.py` (misc client stubs)
- `tg_auto_test/test_utils/serverless_client_admin_stubs.py` (admin client stubs)
- `tg_auto_test/test_utils/serverless_client_auth_stubs.py` (auth client stubs)
- `tg_auto_test/test_utils/serverless_client_iter_stubs.py` (iter client stubs)
- `tg_auto_test/test_utils/serverless_message_metadata.py` (message metadata properties)
- `tg_auto_test/test_utils/serverless_message_serial_stubs.py` (message serial stubs)
- `tg_auto_test/test_utils/serverless_message_properties.py` (message media properties)
- `tg_auto_test/test_utils/serverless_bot_callback_answer.py` (BotCallbackAnswer)
- `tests/unit/test_telethon_conformance_*.py` (existing conformance tests)
- `tests/unit/test_telethon_reverse_conformance_*.py` (existing reverse conformance tests)
- `tests/unit/test_click_returns_message_bug.py` (issue #25 regression test)
- `tests/unit/test_get_edit_bug.py` (issue #24 regression test)
- `tests/unit/helpers_ptb_app.py` (test application builder)
- `Makefile` (quality gates)
- `ruff.toml` (linter rules)
- `vulture_whitelist.py` (false positive suppressions)
- `pyproject.toml` (dependencies: telethon>=1.42.0, python-telegram-bot>=22.6)

## Contract summary

### What (requirements)

- Conformance tests must enforce return-type parity with Telethon
- Behavioral tests must verify core conversation patterns work correctly
- NotImplementedError stubs must be classified and tracked

### How (architecture)

- New test files in `tests/unit/` using `inspect`, `typing.get_type_hints`, and real PTB handlers
- Parametrized tests for scalable coverage
- Self-updating classification registry that fails on unclassified stubs

## Impact inventory (implementation-facing)

- **Module**: `tests/unit/` (new files only)
- **Interfaces**: N/A (test-only)
- **Data model**: N/A
- **External services**: None
- **Test directory**: `tests/unit/`
