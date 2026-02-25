---
Task ID: `T3`
Title: `Add tests for entity serialization`
Depends on: T2
Parallelizable: yes, with T4, T6
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Add unit tests verifying entity serialization logic: the new `serialize_entities()` function, the `entities` field on `MessageResponse`, and end-to-end serialization of messages with entities through `serialize_message()`.

## Context (contract mapping)

- Requirements: Sprint item "Demo UI testing" — "Test entity serialization in `serialize.py`"
- Architecture: existing test patterns in `tests/unit/test_demo_serialize.py`

## Preconditions

- T2 completed: `serialize_entities.py` exists, `MessageResponse` has `entities` field

## Non-goals

- No frontend tests (those are handled differently in this project)
- No testing of the rendering logic (that's frontend)
- Do not modify production code

## Touched surface (expected files / modules)

- `tests/unit/test_demo_serialize_entities.py` — NEW: entity serialization unit tests
- `tests/unit/test_demo_serialize.py` — may add 1-2 tests for entities in `serialize_message` integration

## Dependencies and sequencing notes

- Depends on T2 (the code under test)
- Can run in parallel with T4 (frontend entities) and T6 (not-joined state) — different files
- T7 depends on this task (final verification)

## Third-party / library research (mandatory for any external dependency)

- **Library**: Telethon entity types (already in project)
  - `MessageEntityBold(offset=0, length=5)` — verified: creates entity with `.offset=0, .length=5`
  - `MessageEntityTextUrl(offset=0, length=5, url='https://example.com')` — verified: `.url` attribute present
  - `MessageEntityPre(offset=0, length=5, language='python')` — verified: `.language` attribute present
  
- **Library**: pytest + pytest-asyncio (already in project)
  - `@pytest.mark.asyncio` decorator for async tests
  - Standard `assert` statements

## Implementation steps (developer-facing)

1. **Assess line count for `test_demo_serialize.py`** (currently 150 lines):
   - Adding entity-related tests to this file would push it over 200 lines
   - Create a separate test file: `tests/unit/test_demo_serialize_entities.py`

2. **Create `tests/unit/test_demo_serialize_entities.py`** with the following tests:

   a. **Test `serialize_entity` with each supported type**:
   - `test_serialize_bold_entity`: `MessageEntityBold(offset=0, length=4)` → `{"type": "bold", "offset": 0, "length": 4}`
   - `test_serialize_italic_entity`: `MessageEntityItalic(offset=5, length=3)` → `{"type": "italic", "offset": 5, "length": 3}`
   - `test_serialize_underline_entity`: `MessageEntityUnderline(...)` → `{"type": "underline", ...}`
   - `test_serialize_strikethrough_entity`: `MessageEntityStrike(...)` → `{"type": "strikethrough", ...}`
   - `test_serialize_code_entity`: `MessageEntityCode(...)` → `{"type": "code", ...}`
   - `test_serialize_pre_entity_with_language`: `MessageEntityPre(offset=0, length=10, language="python")` → includes `"language": "python"`
   - `test_serialize_pre_entity_without_language`: `MessageEntityPre(offset=0, length=10, language="")` → no `language` key
   - `test_serialize_url_entity`: `MessageEntityUrl(...)` → `{"type": "url", ...}`
   - `test_serialize_text_url_entity`: `MessageEntityTextUrl(offset=0, length=5, url="https://example.com")` → includes `"url": "https://example.com"`
   - `test_serialize_spoiler_entity`: `MessageEntitySpoiler(...)` → `{"type": "spoiler", ...}`

   b. **Test `serialize_entity` with unsupported type**:
   - `test_serialize_unsupported_entity_returns_none`: pass a `MessageEntityMention(offset=0, length=5)` or similar → returns `None`

   c. **Test `serialize_entities` (list function)**:
   - `test_serialize_entities_none_input`: `serialize_entities(None)` → `[]`
   - `test_serialize_entities_empty_list`: `serialize_entities([])` → `[]`
   - `test_serialize_entities_mixed_types`: list with bold + unsupported → filters out unsupported, returns only bold
   - `test_serialize_entities_multiple`: list with bold + italic + text_url → all three serialized correctly

   d. **Test entity serialization integration with `serialize_message`**:
   - `test_serialize_message_with_entities`: create a mock message with `.entities` containing `[MessageEntityBold(offset=0, length=5)]` and `.text = "Hello world"` → result.entities has the bold entity
   - `test_serialize_message_without_entities`: standard text message with no entities → result.entities is `[]`

3. **Consider whether to add a test in `test_demo_serialize.py`**:
   - The existing file is at 150 lines. Adding a single integration test that checks `entities` field on an existing test would push to ~160, still safe.
   - Add one assertion to `test_serialize_text_message` to verify `result.entities == []` for a plain text message — this is a single line addition.

4. **Mock message with entities for integration test**:
   - The `ServerlessMessage` class does NOT have an `entities` field (it's not a Telethon `Message`)
   - For the integration test, use `unittest.mock.Mock()` to create a message with `.entities` attribute set to a list of Telethon entity objects, plus the standard `.text`, `.id`, `.photo`, `.document`, `.voice`, `.video_note`, `.buttons`, `.poll`, `.invoice` attributes
   - OR: simply set `getattr` behavior using a custom mock, similar to how `test_serialize_invoice_message` works

5. **Run `make check`** to verify all tests pass and lint is green.

## Production safety constraints (mandatory)

- **Database operations**: N/A — no database
- **Resource isolation**: N/A — test-only changes
- **Migration preparation**: N/A

## Anti-disaster constraints (mandatory)

- **Reuse before build**: follows existing test patterns from `test_demo_serialize.py`
- **Correct libraries only**: pytest, telethon (already in project)
- **Correct file locations**: `tests/unit/test_demo_serialize_entities.py` follows naming convention of existing test files
- **No regressions**: only adding new tests; existing tests unchanged (except possibly one assertion addition)
- **Follow UX/spec**: N/A — backend tests

## Error handling + correctness rules (mandatory)

- **Do not silence errors**: tests must assert specific outputs, not catch/ignore exceptions
- Tests must cover the edge case of unsupported entity types
- Tests must verify `None` input handling

## Zero legacy tolerance rule (mandatory)

After implementing this task:
- No dead test code
- No commented-out tests
- All new tests follow existing conventions

## Acceptance criteria (testable)

1. `tests/unit/test_demo_serialize_entities.py` exists with tests for all 9 supported entity types
2. Tests cover `serialize_entity()` returning `None` for unsupported types
3. Tests cover `serialize_entities()` with `None` and empty list inputs
4. Tests cover `serialize_entities()` with mixed supported/unsupported entities
5. Integration test verifies `serialize_message()` populates `entities` field
6. `test_demo_serialize.py` verifies plain text messages have `entities == []`
7. All new tests pass: `uv run pytest tests/unit/test_demo_serialize_entities.py -v`
8. `make check` passes
9. `test_demo_serialize_entities.py` is under 200 lines

## Verification / quality gates

- [ ] Unit tests added/updated — this IS the test task
- [ ] Linters/formatters pass — `make check` green
- [ ] No new warnings introduced
- [ ] Negative-path tests exist — unsupported entity type test, None input test

## Edge cases

- `MessageEntityPre` with empty string language — should NOT include `language` key in output
- Entity type not in `ENTITY_TYPE_MAP` — should be filtered out, not raise
- Message with `entities=None` (no attribute) — should produce empty list via `getattr` default
- `MessageEntityTextUrl` always has `.url` — must be included in output

## Notes / risks

- **Risk**: `test_demo_serialize.py` is at 150 lines; adding too many tests would push it over
  - **Mitigation**: Only add 1 assertion (1 line) to existing file; new tests go in separate file
- **Risk**: Creating mock messages with `.entities` attribute requires careful setup
  - **Mitigation**: Use `unittest.mock.Mock()` with `spec` or manual attribute setting, following existing patterns in `test_demo_serialize.py`
