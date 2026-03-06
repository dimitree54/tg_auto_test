---
Task ID: `T3`
Title: `Add NotImplementedError stub classification and tracking tests`
Sprint: `2026-03-06_qa-improvements`
Module: `tests/unit`
Depends on: `--`
Parallelizable: `yes, with T1 and T2`
Owner: `Developer`
Status: `planned`
---

## Goal / value

A new test file maintains a classification registry of all `NotImplementedError` stubs in the
codebase, distinguishing "could implement but haven't yet" (IMPLEMENTABLE) from "fundamentally
requires external resources" (UNIMPLEMENTABLE). The test auto-detects new unclassified stubs
and fails until they're categorized, preventing stubs from silently accumulating.

## Context (contract mapping)

- Requirements: `CONTRIBUTING.md` ("Unimplemented methods raise NotImplementedError", "never a silent no-op")
- Issue #24: `get_edit()` was left as NotImplementedError stub even though it was implementable
- Source files with stubs:
  - `tg_auto_test/test_utils/serverless_telegram_conversation.py` (conversation stubs)
  - `tg_auto_test/test_utils/serverless_message.py` (message method stubs)
  - `tg_auto_test/test_utils/serverless_message_metadata.py` (message property stubs)
  - `tg_auto_test/test_utils/serverless_message_serial_stubs.py` (TL protocol stubs)
  - `tg_auto_test/test_utils/serverless_client_misc_stubs.py` (client misc stubs)
  - `tg_auto_test/test_utils/serverless_client_admin_stubs.py` (client admin stubs)
  - `tg_auto_test/test_utils/serverless_client_auth_stubs.py` (client auth stubs)
  - `tg_auto_test/test_utils/serverless_client_iter_stubs.py` (client iter stubs)
  - `tg_auto_test/test_utils/serverless_telegram_client_core.py` (get_entity stub)

## Preconditions

- Full understanding of which stubs are implementable in serverless mode vs which require
  external resources (Telegram API, event system, entity resolution, etc.)

## Non-goals

- Implementing any of the IMPLEMENTABLE stubs (separate work)
- Changing any stub implementations
- Adding new stubs

## Module boundary constraints (STRICTLY ENFORCED)

**ALLOWED - this task may ONLY touch:**
- `tests/unit/test_stub_classification.py` - new test file (main registry + tests)
- `tests/unit/stub_classification_registry.py` - new helper (classification data)
- `vulture_whitelist.py` - only if vulture raises false positives on new symbols

**FORBIDDEN - this task must NEVER touch:**
- `tg_auto_test/` source code
- Existing test files
- Linter configuration

**Test scope:**
- Tests go in: `tests/unit/`
- Test command: `uv run pytest tests/unit/test_stub_classification.py -x -v`
- Full validation: `make check`

## Touched surface (expected files / modules)

- `tests/unit/test_stub_classification.py` (new)
- `tests/unit/stub_classification_registry.py` (new - classification data)

## Dependencies and sequencing notes

- No dependencies on T1 or T2
- Can run in parallel with both

## Third-party / library research

- **Library**: `ast` (stdlib, Python 3.12+)
  - `ast.parse()` - parse Python source to AST
  - `ast.walk()` - iterate all nodes in AST
  - `ast.Raise` - node type for `raise` statements
  - `ast.FunctionDef` / `ast.AsyncFunctionDef` - function/method definitions
  - Reference: https://docs.python.org/3.12/library/ast.html

- **Library**: `pathlib` (stdlib, Python 3.12+)
  - `Path.glob("**/*.py")` - recursive file search
  - Reference: https://docs.python.org/3.12/library/pathlib.html

## Implementation steps

1. **Create `tests/unit/stub_classification_registry.py`** containing the classification data.

2. **Define the classification enum and registry:**
   ```python
   from enum import Enum

   class StubCategory(Enum):
       IMPLEMENTABLE = "implementable"
       UNIMPLEMENTABLE = "unimplementable"
   ```

3. **Build the classification registry** as a dict keyed by `(module_path, method_name)`:

   **Conversation stubs** (`serverless_telegram_conversation.py`):
   - `("serverless_telegram_conversation", "get_reply")` -> IMPLEMENTABLE
   - `("serverless_telegram_conversation", "cancel")` -> UNIMPLEMENTABLE
   - `("serverless_telegram_conversation", "cancel_all")` -> UNIMPLEMENTABLE
   - `("serverless_telegram_conversation", "wait_event")` -> UNIMPLEMENTABLE
   - `("serverless_telegram_conversation", "wait_read")` -> UNIMPLEMENTABLE
   - `("serverless_telegram_conversation", "mark_read")` -> UNIMPLEMENTABLE
   - `("serverless_telegram_conversation", "chat")` -> IMPLEMENTABLE
   - `("serverless_telegram_conversation", "chat_id")` -> IMPLEMENTABLE
   - `("serverless_telegram_conversation", "input_chat")` -> UNIMPLEMENTABLE
   - `("serverless_telegram_conversation", "is_channel")` -> IMPLEMENTABLE
   - `("serverless_telegram_conversation", "is_group")` -> IMPLEMENTABLE
   - `("serverless_telegram_conversation", "is_private")` -> IMPLEMENTABLE
   - `("serverless_telegram_conversation", "get_chat")` -> UNIMPLEMENTABLE
   - `("serverless_telegram_conversation", "get_input_chat")` -> UNIMPLEMENTABLE

   **Message method stubs** (`serverless_message.py`):
   - `("serverless_message", "delete")` -> UNIMPLEMENTABLE
   - `("serverless_message", "edit")` -> UNIMPLEMENTABLE
   - `("serverless_message", "reply")` -> UNIMPLEMENTABLE
   - `("serverless_message", "forward_to")` -> UNIMPLEMENTABLE
   - `("serverless_message", "get_reply_message")` -> UNIMPLEMENTABLE
   - `("serverless_message", "get_buttons")` -> IMPLEMENTABLE
   - `("serverless_message", "get_chat")` -> UNIMPLEMENTABLE
   - `("serverless_message", "get_entities_text")` -> IMPLEMENTABLE
   - `("serverless_message", "get_input_chat")` -> UNIMPLEMENTABLE
   - `("serverless_message", "get_input_sender")` -> UNIMPLEMENTABLE
   - `("serverless_message", "get_sender")` -> UNIMPLEMENTABLE
   - `("serverless_message", "mark_read")` -> UNIMPLEMENTABLE
   - `("serverless_message", "pin")` -> UNIMPLEMENTABLE
   - `("serverless_message", "respond")` -> UNIMPLEMENTABLE
   - `("serverless_message", "unpin")` -> UNIMPLEMENTABLE

   **Message metadata stubs** (`serverless_message_metadata.py`):
   - `("serverless_message_metadata", "sender")` -> UNIMPLEMENTABLE
   - `("serverless_message_metadata", "chat")` -> UNIMPLEMENTABLE
   - `("serverless_message_metadata", "action_entities")` -> UNIMPLEMENTABLE
   - `("serverless_message_metadata", "geo")` -> UNIMPLEMENTABLE
   - `("serverless_message_metadata", "is_reply")` -> IMPLEMENTABLE
   - `("serverless_message_metadata", "reply_to_chat")` -> UNIMPLEMENTABLE
   - `("serverless_message_metadata", "reply_to_sender")` -> UNIMPLEMENTABLE
   - `("serverless_message_metadata", "to_id")` -> UNIMPLEMENTABLE
   - `("serverless_message_metadata", "via_input_bot")` -> UNIMPLEMENTABLE
   - `("serverless_message_metadata", "client")` -> UNIMPLEMENTABLE
   - `("serverless_message_metadata", "input_chat")` -> UNIMPLEMENTABLE
   - `("serverless_message_metadata", "input_sender")` -> UNIMPLEMENTABLE
   - `("serverless_message_metadata", "is_channel")` -> IMPLEMENTABLE
   - `("serverless_message_metadata", "is_group")` -> IMPLEMENTABLE
   - `("serverless_message_metadata", "is_private")` -> IMPLEMENTABLE

   **Message serial stubs** (`serverless_message_serial_stubs.py`):
   - `("serverless_message_serial_stubs", "from_reader")` -> UNIMPLEMENTABLE
   - `("serverless_message_serial_stubs", "serialize_bytes")` -> UNIMPLEMENTABLE
   - `("serverless_message_serial_stubs", "serialize_datetime")` -> UNIMPLEMENTABLE
   - `("serverless_message_serial_stubs", "to_dict")` -> IMPLEMENTABLE
   - `("serverless_message_serial_stubs", "to_json")` -> IMPLEMENTABLE
   - `("serverless_message_serial_stubs", "stringify")` -> IMPLEMENTABLE
   - `("serverless_message_serial_stubs", "pretty_format")` -> IMPLEMENTABLE

   **Client stubs** (across multiple files):
   - All methods in `serverless_client_misc_stubs.py` -> UNIMPLEMENTABLE
   - All methods in `serverless_client_admin_stubs.py` -> UNIMPLEMENTABLE
   - All methods in `serverless_client_auth_stubs.py` -> UNIMPLEMENTABLE
   - All methods in `serverless_client_iter_stubs.py` -> UNIMPLEMENTABLE
   - `("serverless_telegram_client_core", "get_entity")` -> UNIMPLEMENTABLE

   Note: Methods that raise `NotImplementedError` for unsupported *parameters* (like
   `download_media(thumb=...)` or `send_message(reply_to=...)`) are NOT stubs - they are
   partial implementations. Only classify methods where the *entire method body* raises
   `NotImplementedError`.

4. **Create `tests/unit/test_stub_classification.py`** with three test functions:

   a. **`test_all_stubs_are_classified`**: Use `ast` to scan all `.py` files under
      `tg_auto_test/test_utils/` for methods/properties whose body is exclusively a
      `raise NotImplementedError(...)`. Compare against the registry. Fail with a clear
      message listing any unclassified stubs.

   b. **`test_no_stale_classifications`**: For each entry in the registry, verify the
      corresponding method still raises `NotImplementedError`. If someone implemented a
      stub (removed the `raise`), the test fails until the entry is removed from the
      registry.

   c. **`test_implementable_count_is_tracked`**: Assert the exact count of IMPLEMENTABLE
      stubs. When someone implements one and removes it from the registry, this count
      must be updated. This provides visibility into the "debt" of unimplemented features.

5. **AST scanning logic** (in the test file or a helper):
   - Parse each `.py` file with `ast.parse()`
   - Walk the AST looking for `FunctionDef` / `AsyncFunctionDef` nodes
   - Check if the function body is exclusively `raise NotImplementedError(...)` (possibly
     preceded by `del` statements for unused parameters)
   - Extract module name (from filename) and method name
   - Skip methods that have substantive logic before the raise (these are partial
     implementations, not pure stubs)

6. **Ensure files stay under 200 lines.** The registry data is large (~80+ entries).
   Split into two files:
   - `tests/unit/stub_classification_registry.py` - the enum + dict (~120 lines)
   - `tests/unit/test_stub_classification.py` - the test functions + AST scanner (~150 lines)

7. **Run `make check`** to verify all quality gates pass.

## Production safety constraints

N/A - test-only files, no runtime or database impact.

## Anti-disaster constraints

- **Reuse before build**: Use `ast` stdlib (no external AST libraries)
- **Correct libraries only**: Only `ast`, `pathlib`, `enum` (all stdlib)
- **Correct file locations**: `tests/unit/test_stub_classification.py`, `tests/unit/stub_classification_registry.py`
- **No regressions**: New test files only; no modification to existing code

## Error handling + correctness rules

- AST parsing errors must propagate (no `try/except` around `ast.parse`)
- If a source file can't be parsed, the test should fail loudly
- Registry mismatches produce clear assertion messages listing each offending method

## Zero legacy tolerance rule

- No placeholder entries in the registry
- No commented-out classifications
- Every registry entry must correspond to an actual `NotImplementedError` in the codebase

## Acceptance criteria (testable)

1. `tests/unit/test_stub_classification.py` and `tests/unit/stub_classification_registry.py` exist
2. Registry contains every `NotImplementedError` stub from the source files listed above
3. `test_all_stubs_are_classified` passes (no unclassified stubs)
4. `test_no_stale_classifications` passes (no entries for methods that no longer raise)
5. `test_implementable_count_is_tracked` passes (correct count of IMPLEMENTABLE stubs)
6. Adding a new `NotImplementedError` stub without updating the registry causes test failure
7. Implementing a stub (removing `NotImplementedError`) without updating the registry causes test failure
8. `uv run pytest tests/unit/test_stub_classification.py -x -v` passes
9. `make check` passes 100%
10. Both files are under 200 lines each

## Verification / quality gates

- [ ] New test files created in `tests/unit/`
- [ ] Tests pass: `uv run pytest tests/unit/test_stub_classification.py -x -v`
- [ ] `make check` passes 100%
- [ ] Both files under 200 lines (pylint C0302)
- [ ] No new vulture warnings (or whitelist updated)
- [ ] No ruff violations
- [ ] AST scanner covers all source files listed in context

## Edge cases

- Method body has `del param; raise NotImplementedError(...)` - still a pure stub (the `del` is for unused params)
- Method body has conditional logic before `raise` (like `if param: raise NotImplementedError("param not supported")`) - this is a partial implementation, NOT a pure stub
- Property stubs (using `@property` decorator) - must be detected alongside regular methods
- `@classmethod` and `@staticmethod` stubs - must be detected
- Nested functions inside methods - should NOT be classified (only top-level class methods)
- Files outside `tg_auto_test/test_utils/` - should NOT be scanned (the stubs live only there)

## Notes / risks

- **Risk**: AST detection of "pure stubs" may miss edge cases where the body has more than just `raise`.
  - **Mitigation**: Define "pure stub" strictly: method body is one or more `del` statements followed by exactly one `raise NotImplementedError(...)`. Any other pattern is a partial implementation and excluded.
- **Risk**: The registry file may approach 200 lines as stubs accumulate.
  - **Mitigation**: The registry uses a compact dict format. Currently ~80 entries fit in ~120 lines. If the codebase grows significantly, the registry can be split by source module.
- **Risk**: `ruff` may flag unused imports in the registry file.
  - **Mitigation**: The enum and dict are imported by the test file. Verify imports are used.
