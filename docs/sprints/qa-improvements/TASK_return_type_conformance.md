---
Task ID: `T1`
Title: `Add return-type annotation conformance tests`
Sprint: `2026-03-06_qa-improvements`
Module: `tests/unit`
Depends on: `--`
Parallelizable: `yes, with T2 and T3`
Owner: `Developer`
Status: `planned`
---

## Goal / value

A new test file verifies that return-type annotations of implemented methods on our
fake classes match Telethon's. This would have caught issue #25 (`click()` annotated as
returning `ServerlessMessage` instead of `BotCallbackAnswer`) before it reached consumers.

## Context (contract mapping)

- Requirements: `CONTRIBUTING.md` ("Conformance tests enforce parity", "interfaces MUST match Telethon's public signatures exactly")
- Existing conformance tests: `tests/unit/test_telethon_conformance_*.py` (check param names/kinds only)
- Issue #25 regression test: `tests/unit/test_click_returns_message_bug.py`

## Preconditions

- Telethon >= 1.42.0 installed (already in `pyproject.toml`)
- Understanding of which Telethon methods have concrete signatures vs `(*args, **kwargs)` wrappers

## Non-goals

- Fixing return-type mismatches discovered by these tests (separate work; use `xfail(strict=True)` for known issues)
- Testing parameter types (already covered by existing conformance tests)
- Testing methods with `(*args, **kwargs)` signatures in Telethon (no useful return annotation available)

## Module boundary constraints (STRICTLY ENFORCED)

**ALLOWED - this task may ONLY touch:**
- `tests/unit/test_telethon_return_type_conformance.py` - new test file
- `vulture_whitelist.py` - only if vulture raises false positives on new symbols

**FORBIDDEN - this task must NEVER touch:**
- `tg_auto_test/` source code
- Existing test files
- Linter configuration

**Test scope:**
- Tests go in: `tests/unit/`
- Test command: `uv run pytest tests/unit/test_telethon_return_type_conformance.py -x -v`
- Full validation: `make check`

## Touched surface (expected files / modules)

- `tests/unit/test_telethon_return_type_conformance.py` (new)

## Dependencies and sequencing notes

- No dependencies on T2 or T3
- Can run in parallel with both

## Third-party / library research

- **Library**: `inspect` (stdlib, Python 3.12+)
  - `inspect.signature(method).return_annotation` returns the annotation object or `inspect.Parameter.empty`
  - For methods defined with `(*args, **kwargs)`, `return_annotation` is typically `inspect.Parameter.empty`
  - Reference: https://docs.python.org/3.12/library/inspect.html#inspect.Signature.return_annotation

- **Library**: `typing.get_type_hints()` (stdlib, Python 3.12+)
  - Resolves string annotations and forward references
  - Raises `NameError` if forward references can't be resolved - use `inspect.signature` as fallback
  - Reference: https://docs.python.org/3.12/library/typing.html#typing.get_type_hints

- **Library**: Telethon 1.42.x
  - `telethon.tl.custom.conversation.Conversation` - has concrete signatures for `get_response`, `get_edit`, `get_reply`, `send_message`, `send_file`
  - `telethon.tl.custom.message.Message` - has concrete signature for `click()`, `download_media()`; uses `(*args, **kwargs)` for `delete`, `edit`, `reply`, `respond`, `forward_to`
  - `telethon.TelegramClient` - has concrete signatures for `conversation()`, `get_me()`, `get_messages()`, `get_entity()`, `send_message()`, `send_file()`, `download_media()`
  - Source: https://github.com/LonamiWebs/Telethon/tree/v1/telethon

## Implementation steps

1. **Create `tests/unit/test_telethon_return_type_conformance.py`.**

2. **Write a helper function** that extracts the return annotation from a method:
   ```python
   def _get_return_annotation(cls, method_name):
       sig = inspect.signature(getattr(cls, method_name))
       return sig.return_annotation
   ```

3. **Define the list of methods with concrete Telethon signatures** (skip `(*args, **kwargs)` methods):

   **Conversation methods** (from `telethon.tl.custom.conversation.Conversation`):
   - `get_response()` - Telethon returns `Message`
   - `get_edit()` - Telethon returns `Message`
   - `get_reply()` - Telethon returns `Message`
   - `send_message()` - Telethon returns `Message`
   - `send_file()` - Telethon returns `Message`

   **Message methods** (from `telethon.tl.custom.message.Message`):
   - `click()` - Telethon signature returns explicit type (NOT `(*args, **kwargs)`)
   - `download_media()` - concrete signature
   - `get_reply_message()` - concrete signature

   **Client methods** (from `telethon.TelegramClient`):
   - `conversation()` - returns `Conversation`
   - `get_me()` - returns `User`
   - `get_messages()` - returns messages
   - `get_entity()` - returns entity
   - `send_message()` - returns `Message`
   - `send_file()` - returns `Message`
   - `download_media()` - returns file path/bytes

4. **Write parametrized conformance tests** structured as:

   ```python
   class TestReturnTypeConformance:
       @pytest.mark.parametrize("method_name", [...])
       def test_conversation_return_type_matches(self, method_name):
           telethon_annotation = _get_return_annotation(Conversation, method_name)
           our_annotation = _get_return_annotation(ServerlessTelegramConversation, method_name)
           # Skip if Telethon has no annotation (empty)
           if telethon_annotation is inspect.Parameter.empty:
               return
           # Verify our annotation is not empty when Telethon's is present
           assert our_annotation is not inspect.Parameter.empty
   ```

5. **Add specific regression tests** for known issues:
   - `test_click_return_type_is_not_serverless_message`: verify `ServerlessMessage.click` return annotation is `ServerlessBotCallbackAnswer`, not `ServerlessMessage`
   - `test_get_response_return_type`: verify `ServerlessTelegramConversation.get_response` return annotation is `ServerlessMessage` (matching Telethon's `Message`)

6. **Ensure file stays under 200 lines.** If it exceeds ~180 lines, decompose into:
   - `test_telethon_return_type_conformance.py` (parametrized test runner)
   - A helper module if needed for annotation extraction logic

7. **Run `make check`** to verify all quality gates pass.

## Production safety constraints

N/A - test-only file, no runtime or database impact.

## Anti-disaster constraints

- **Reuse before build**: Use `inspect.signature` patterns already established in existing conformance tests
- **Correct libraries only**: Only `inspect` (stdlib) and `typing` (stdlib) - no new dependencies
- **Correct file locations**: New file goes in `tests/unit/` following existing naming convention (`test_telethon_*`)
- **No regressions**: New tests only; no modification to existing tests or source

## Error handling + correctness rules

- If `typing.get_type_hints()` raises `NameError` for a class, fall back to `inspect.signature().return_annotation`
- If a method doesn't exist on either class, fail with a clear assertion message
- No try/except blocks that swallow errors

## Zero legacy tolerance rule

- No dead code in the new test file
- No commented-out test cases
- No placeholder "TODO" assertions

## Acceptance criteria (testable)

1. `tests/unit/test_telethon_return_type_conformance.py` exists and contains parametrized tests
2. `ServerlessMessage.click()` return annotation is verified to be `ServerlessBotCallbackAnswer` (not `ServerlessMessage`)
3. `ServerlessTelegramConversation.get_response()`, `get_edit()`, `get_reply()` return annotations are verified
4. Client methods `conversation()`, `get_me()`, `get_messages()` return annotations are verified
5. Methods with `(*args, **kwargs)` in Telethon are excluded (no false failures)
6. `uv run pytest tests/unit/test_telethon_return_type_conformance.py -x -v` passes
7. `make check` passes 100%
8. File is under 200 lines

## Verification / quality gates

- [ ] New test file created in `tests/unit/`
- [ ] Tests pass: `uv run pytest tests/unit/test_telethon_return_type_conformance.py -x -v`
- [ ] `make check` passes 100%
- [ ] File under 200 lines (pylint C0302)
- [ ] No new vulture warnings (or whitelist updated)
- [ ] No ruff violations

## Edge cases

- Telethon method has return annotation but our fake doesn't (test should flag this)
- Telethon method uses forward reference strings in annotations (use `typing.get_type_hints` to resolve)
- Property return annotations vs method return annotations (handle both via `inspect.signature`)
- `inspect.Parameter.empty` when Telethon uses `(*args, **kwargs)` - skip these methods

## Notes / risks

- **Risk**: Some Telethon return annotations use internal types that don't map cleanly to our types.
  - **Mitigation**: Test for compatibility (not identity). For example, if Telethon returns `Message` and we return `ServerlessMessage`, that's acceptable since our class is a substitute. The test should catch cases where the return type is fundamentally wrong (e.g., `ServerlessMessage` instead of `BotCallbackAnswer`).
