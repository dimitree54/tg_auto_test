---
Task ID: `T1`
Title: `Add reverse conformance tests for all 4 fake classes`
Depends on: —
Parallelizable: no (foundation task — all other tasks depend on this)
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Create auto-detecting reverse conformance tests that verify every public method/attribute on real Telethon classes also exists on our fake classes. These tests will fail for all ~86 missing members, serving as both the acceptance test and the authoritative source for what stubs T4–T6 must add.

## Context (contract mapping)

- Requirements: User's GAP 1 — "Reverse Conformance Tests" section
- Architecture: Existing conformance tests in `tests/unit/test_telethon_conformance_*.py` only check the forward direction ("our fakes don't have EXTRA methods"). This task adds the reverse.

## Preconditions

- `make check` is green (baseline confirmed)
- Existing forward conformance tests pass

## Non-goals

- Adding stubs to make the reverse tests pass (that's T4–T6)
- Changing existing forward conformance tests

## Touched surface (expected files / modules)

- `tests/unit/test_telethon_reverse_conformance_client.py` (NEW)
- `tests/unit/test_telethon_reverse_conformance_message.py` (NEW)
- `tests/unit/test_telethon_reverse_conformance_conversation.py` (NEW)
- `tests/unit/test_telethon_reverse_conformance_button.py` (NEW)

## Dependencies and sequencing notes

- No dependencies — this is the foundation task.
- Cannot run in parallel with other tasks because its test failures define the work for T4–T6.
- Tests will initially be marked `pytest.mark.xfail(strict=True)` since the stubs don't exist yet. T4–T6 remove xfail markers as stubs are added.

## Third-party / library research

- **Library**: Telethon 1.42.x (version in `uv.lock`)
- **Relevant classes**:
  - `telethon.TelegramClient` — https://docs.telethon.dev/en/stable/modules/client.html
  - `telethon.tl.custom.Message` — https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.message.Message
  - `telethon.tl.custom.Conversation` — https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.conversation.Conversation
  - `telethon.tl.custom.MessageButton` — https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.messagebutton.MessageButton
- **Introspection approach**: Use `dir(RealClass)` to get all public names (not starting with `_`), then filter to only callable or property members using `inspect.isfunction`, `inspect.ismethod`, or `isinstance(getattr(cls, name), property)`. Use `hasattr(FakeClass, name)` to check existence.
- **Known gotcha**: Telethon's `Message` inherits from `ChatGetter`, `SenderGetter`, and `TLObject`. Many public attributes come from these mixins, including TL-protocol internals like `CONSTRUCTOR_ID`, `SUBCLASS_OF_ID`, `from_reader`, `serialize_bytes`, `serialize_datetime`, `to_dict`, `to_json`, `stringify`, `pretty_format`. These are legitimate public attributes that need stubs OR allowlist entries.

## Implementation steps (developer-facing)

1. **Create `tests/unit/test_telethon_reverse_conformance_client.py`**:
   - Import `TelegramClient` from `telethon` and `ServerlessTelegramClientCore` from our library.
   - Write a helper function `_get_public_members(cls)` that returns a set of names from `dir(cls)` where `not name.startswith("_")`.
   - Define an `ALLOWLIST` set of Telethon-only members we intentionally skip, with a comment for each explaining why (e.g., `{"session"}` — "connection-level attribute, not applicable to serverless testing").
   - Write a parametrized test: for each member in `_get_public_members(TelegramClient) - ALLOWLIST`, assert `hasattr(ServerlessTelegramClientCore, member)` OR `hasattr(ServerlessTelegramClient, member)` (check both classes since some methods like `get_input_entity` live on the subclass).
   - Mark the parametrized test with `pytest.mark.xfail(strict=True)` initially (these will fail until T4 adds stubs). **Important**: use parametrize so each missing method is a separate xfail test case, making progress trackable.
   - Also write a non-xfail meta-test that verifies the allowlist doesn't contain names that DON'T exist on Telethon (stale allowlist detection).

2. **Create `tests/unit/test_telethon_reverse_conformance_message.py`**:
   - Same pattern as client, but comparing `telethon.tl.custom.Message` vs `ServerlessMessage`.
   - The allowlist will likely include TL-protocol internals: `CONSTRUCTOR_ID`, `SUBCLASS_OF_ID`, `from_reader`, `serialize_bytes`, `serialize_datetime` — but the developer should confirm by running the test first and examining which names are truly protocol-internal vs. user-facing.
   - Mark missing members as xfail. T5 removes xfail markers.

3. **Create `tests/unit/test_telethon_reverse_conformance_conversation.py`**:
   - Same pattern comparing `telethon.tl.custom.Conversation` vs `ServerlessTelegramConversation`.
   - Mark missing members as xfail. T6 removes xfail markers.

4. **Create `tests/unit/test_telethon_reverse_conformance_button.py`**:
   - Same pattern comparing `telethon.tl.custom.MessageButton` vs `ServerlessButton`.
   - Mark missing members as xfail. T6 removes xfail markers.

5. **Run `make check`** — must be 100% green. All xfail tests should xfail (not unexpectedly pass), and all non-xfail tests should pass.

6. **Record the exact list of missing members per class** by running the tests with `-v` and noting which parametrized cases xfail. This list is the authoritative input for T4–T6.

## Production safety constraints (mandatory)

N/A — testing library, no production resources.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: Follows the existing conformance test pattern in `tests/unit/test_telethon_conformance_*.py`.
- **Correct file locations**: New files in `tests/unit/` following the `test_telethon_conformance_*` naming convention.
- **No regressions**: Existing tests unchanged; new tests are xfail so `make check` stays green.

## Error handling + correctness rules (mandatory)

- No error handling needed — these are pure assertion tests.
- Tests must not swallow assertion errors or use bare `except`.

## Zero legacy tolerance rule (mandatory)

- No legacy impact — this task only adds new test files.

## Acceptance criteria (testable)

1. Four new test files exist in `tests/unit/`:
   - `test_telethon_reverse_conformance_client.py`
   - `test_telethon_reverse_conformance_message.py`
   - `test_telethon_reverse_conformance_conversation.py`
   - `test_telethon_reverse_conformance_button.py`
2. Each file contains a parametrized test that checks every public Telethon member exists on our fake class.
3. Each file contains an allowlist with documented reasons for each skipped member.
4. Each file contains a stale-allowlist meta-test.
5. All new tests are marked `pytest.mark.xfail(strict=True)` for missing members.
6. `make check` is 100% green (xfail tests xfail as expected).
7. Each test file is under 200 lines.
8. Running with `-v` produces a clear list of missing members per class.

## Verification / quality gates

- [ ] `make check` passes (ruff format, ruff check, pylint 200-line limit, vulture, jscpd, pytest)
- [ ] `uv run pytest tests/unit/test_telethon_reverse_conformance_client.py -v` shows xfail for each missing client member
- [ ] `uv run pytest tests/unit/test_telethon_reverse_conformance_message.py -v` shows xfail for each missing message member
- [ ] `uv run pytest tests/unit/test_telethon_reverse_conformance_conversation.py -v` shows xfail for each missing conversation member
- [ ] `uv run pytest tests/unit/test_telethon_reverse_conformance_button.py -v` shows xfail for each missing button member
- [ ] No new warnings introduced

## Edge cases

- Some Telethon "public" names may be class-level constants (e.g., `CONSTRUCTOR_ID`) — the test should still check them via `hasattr` since they're part of the public API. If we decide to skip them, add to allowlist with reason.
- Properties and methods should both be covered by `hasattr` — no need to distinguish.
- Telethon may have public names that are actually inherited from `object` (e.g., `__class__` is filtered by the `_` prefix check). Confirm the `dir()` output is clean.

## Notes / risks

- **Risk**: The parametrized xfail tests might produce very long test output. This is expected and useful — each xfail is a specific missing member.
  - **Mitigation**: The `-v` output serves as the authoritative list for T4–T6.
- **Risk**: Telethon version differences may change the public API.
  - **Mitigation**: Tests introspect at runtime, so they automatically adapt. If Telethon adds a new method, the test will catch it in CI.
