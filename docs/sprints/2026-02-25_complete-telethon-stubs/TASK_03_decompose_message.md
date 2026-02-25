---
Task ID: `T3`
Title: `Extract message media properties into a mixin to free space in serverless_message.py`
Depends on: —
Parallelizable: yes, with T1, T2, T6
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Create `serverless_message_properties.py` containing a `ServerlessMessageProperties` mixin class. Move media-related property methods (`photo`, `document`, `voice`, `video_note`, `file`, `invoice`, `poll`, `buttons`, `button_count`) from `ServerlessMessage` into this mixin. This frees ~80 lines in `serverless_message.py` for T4 (new properties) and T5 (new methods).

## Context (contract mapping)

- Requirements: Need to add ~19 new properties and 5 new methods to ServerlessMessage; current file is 197 lines
- Architecture: `AGENTS.md` mandates files stay under 200 lines; decompose rather than compact

## Preconditions

- `make check` is green (baseline confirmed)
- `serverless_message.py` is 197 lines

## Non-goals

- Adding new properties (that's T4)
- Adding new methods (that's T5)
- Changing any behavior of existing properties

## Touched surface (expected files / modules)

- `tg_auto_test/test_utils/serverless_message_properties.py` (NEW — ~90 lines)
- `tg_auto_test/test_utils/serverless_message.py` (modify — remove extracted properties, inherit from mixin)

## Dependencies and sequencing notes

- No dependencies; pure refactoring with no behavior change.
- Can run in parallel with T1 (client decomposition) and T6 (conversation stubs) — different files.
- T4 and T5 depend on T3 completing.

## Third-party / library research

No third-party libraries involved. This is internal refactoring.

The mixin needs these telethon imports (moved from serverless_message.py):
- `from telethon.tl.custom.file import File as TelethonFile`
- `from telethon.tl.types import Document, DocumentAttributeAudio, DocumentAttributeVideo, MessageMediaInvoice, MessageMediaPoll, Photo`
- `from tg_auto_test.test_utils.model_helpers import build_poll_media`
- `from tg_auto_test.test_utils.serverless_button import ServerlessButton`
- `from tg_auto_test.test_utils.serverless_message_helpers import ReplyMarkup`

## Implementation steps (developer-facing)

1. **Create `tg_auto_test/test_utils/serverless_message_properties.py`**:
   - Define class `ServerlessMessageProperties` (no base class; mixin).
   - Move these `@property` methods from `ServerlessMessage`:
     - `photo(self) -> Photo | None` (~3 lines)
     - `document(self) -> Document | None` (~3 lines)
     - `voice(self) -> Document | None` (~7 lines)
     - `video_note(self) -> Document | None` (~7 lines)
     - `file(self) -> TelethonFile | None` (~6 lines)
     - `invoice(self) -> MessageMediaInvoice | None` (~3 lines)
     - `poll(self) -> MessageMediaPoll | None` (~3 lines)
     - `buttons(self) -> list[list[ServerlessButton]] | None` (~8 lines)
     - `button_count(self) -> int` (~5 lines)
   - Also move the module-level helper `_wrap_button_row` function from `serverless_message.py` into this file (it's only used by the `buttons` property).
   - Add the necessary imports at the top of the mixin file.
   - Properties reference `self._media_photo`, `self._media_document`, `self._invoice_data`, `self._poll_data`, `self._file_cache`, `self._reply_markup_data`, `self._raw_bytes`, `self._response_file_id`, `self._file_store` — these are dataclass fields defined on `ServerlessMessage` and available at runtime via MRO.

2. **Modify `serverless_message.py`**:
   - Add import: `from tg_auto_test.test_utils.serverless_message_properties import ServerlessMessageProperties`
   - **Cannot use standard inheritance with `@dataclass(slots=True)`** — slots dataclasses don't support regular mixin inheritance cleanly. Instead, use this pattern:
     - Keep `ServerlessMessage` as `@dataclass(slots=True)` 
     - Make `ServerlessMessageProperties` a regular class (not a dataclass)
     - Add `ServerlessMessageProperties` as a base class: `class ServerlessMessage(ServerlessMessageProperties):`
     - **Important**: When a dataclass with `slots=True` inherits from a non-dataclass, Python creates `__slots__` only for the new fields. The mixin's properties (defined as `@property` on the class) work fine because they're class-level descriptors, not instance attributes.
   - Remove the moved property methods and the `_wrap_button_row` function from `serverless_message.py`.
   - Remove any imports that are now only used in the mixin file.
   - Keep: `__init__` (dataclass), `download_media`, `click`, all dataclass fields.

3. **Verify line counts**:
   - `serverless_message_properties.py`: should be ~90 lines
   - `serverless_message.py`: should drop from 197 to ~100 lines

4. **Run `make check`** — must be 100% green. All existing tests pass unchanged.

## Production safety constraints (mandatory)

N/A — testing library, no production resources.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: extracting existing code, not writing new code.
- **Correct file locations**: new file in `tg_auto_test/test_utils/` following naming convention.
- **No regressions**: all existing tests pass unchanged.

## Error handling + correctness rules (mandatory)

- No error handling changes — properties are moved verbatim.
- No try/catch or fallback behavior added.

## Zero legacy tolerance rule (mandatory)

- After extraction, `serverless_message.py` must not contain the moved properties or `_wrap_button_row`.
- Remove unused imports from `serverless_message.py`.
- The duplicate `_wrap_button_row` in `serverless_message_helpers.py` (lines 21-33) — check if it's still used. If not, consider removing it. If it IS used by `models.py` re-export, leave it. Note: `models.py` imports `_wrap_button_row` from `serverless_message_helpers.py`, not from `serverless_message.py`. The `serverless_message.py` version was a separate copy. After removing it, verify `models.py` import chain still works.

## Acceptance criteria (testable)

1. `serverless_message_properties.py` exists and contains the 9 property methods plus `_wrap_button_row`.
2. `ServerlessMessage` inherits from `ServerlessMessageProperties`.
3. `serverless_message.py` no longer contains the moved property bodies or `_wrap_button_row`.
4. Both files are under 200 lines.
5. `make check` is 100% green (all 110 tests pass, 15 xfail unchanged — or 11 xfail if T2 ran first).

## Verification / quality gates

- [ ] `make check` passes
- [ ] `wc -l` on both files shows < 200
- [ ] No new warnings introduced
- [ ] `jscpd` passes (no code duplication between old/new files)

## Edge cases

- `@dataclass(slots=True)` + mixin inheritance: verify that `ServerlessMessage(id=1, text="hi")` still works as a dataclass.
- `isinstance(msg, ServerlessMessage)` still works.
- `from tg_auto_test.test_utils.models import ServerlessMessage` still works (re-export path unchanged).
- `_file_cache` is mutated inside the `file` property (`self._file_cache = ...`). With slots, this mutation works because `_file_cache` is declared as a slot on `ServerlessMessage`. The property method is on the mixin class but accesses the slot on `self` (the concrete instance).

## Notes / risks

- **Risk**: `@dataclass(slots=True)` with base class — Python 3.10+ handles this correctly: only the new fields get `__slots__`, and the base class can have methods/properties.
  - **Mitigation**: This pattern already works in the codebase (e.g., `ServerlessButton` is frozen+slots). Test thoroughly.
- **Risk**: `_wrap_button_row` exists in both `serverless_message.py` and `serverless_message_helpers.py`. They're slightly different implementations.
  - **Mitigation**: After moving properties to the mixin, the mixin's `buttons` property should use the `_wrap_button_row` that's co-located with it. Verify which version is correct and remove the duplicate.
