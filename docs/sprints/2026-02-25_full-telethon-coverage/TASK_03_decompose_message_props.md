---
Task ID: `T3`
Title: `Split serverless_message_properties.py into multiple mixin files for message stubs`
Depends on: T1
Parallelizable: yes, with T2 and T6
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Decompose `serverless_message_properties.py` (currently 197 lines — nearly at the limit) into multiple logical mixin files so that T5 can add ~32 message stubs without exceeding the 200-line limit in any file.

## Context (contract mapping)

- Requirements: User identified ~32 missing message methods/properties; current file at 197 lines cannot absorb them
- Architecture: `AGENTS.md` mandates 200-line limit with logical decomposition

## Preconditions

- T1 complete (reverse conformance tests identify exact missing message members)
- `make check` is green

## Non-goals

- Adding new stubs (that's T5)
- Changing behavior of existing properties

## Touched surface (expected files / modules)

- `tg_auto_test/test_utils/serverless_message_properties.py` (MODIFY — keep media properties, reduce significantly)
- `tg_auto_test/test_utils/serverless_message_metadata.py` (NEW — extract metadata-related properties)
- `tg_auto_test/test_utils/serverless_message.py` (MODIFY — may need to update MRO if inheritance chain changes)

## Dependencies and sequencing notes

- Depends on T1 so the developer knows the exact list of missing message members and can plan grouping.
- Can run in parallel with T2 (client decomposition) and T6 (conversation/button) since they touch different files.

## Third-party / library research

No third-party libraries involved. Internal refactoring using established mixin pattern.

## Implementation steps (developer-facing)

1. **Analyze T1's output** to confirm exact missing message members. Group the existing + future members logically:
   - **Media properties** (existing, keep in `serverless_message_properties.py`): `photo`, `document`, `voice`, `video_note`, `file`, `invoice`, `poll`, `buttons`, `button_count`, `audio`, `video`
   - **Metadata properties** (existing, extract to new file): `sender`, `sender_id`, `chat`, `chat_id`, `raw_text`, `reply_to_msg_id`, `forward`, `via_bot`, `sticker`, `contact`, `venue`, `gif`, `game`, `web_preview`, `dice`
   - Plus the `_wrap_button_row` helper function stays with `buttons` property.

2. **Create `tg_auto_test/test_utils/serverless_message_metadata.py`** (NEW):
   - Define class `ServerlessMessageMetadata` (mixin, no base class).
   - Move these properties from `serverless_message_properties.py`:
     - `sender`, `sender_id`, `chat`, `chat_id`, `raw_text`, `reply_to_msg_id`
     - `forward`, `via_bot`, `sticker`, `contact`, `venue`, `gif`, `game`, `web_preview`, `dice`
   - These are all simple properties (most return `None` or raise `NotImplementedError`).
   - Target: ~70 lines.

3. **Update `serverless_message_properties.py`**:
   - Inherit from `ServerlessMessageMetadata`: `class ServerlessMessageProperties(ServerlessMessageMetadata):`
   - Remove the extracted properties.
   - Keep: `photo`, `document`, `voice`, `video_note`, `file`, `invoice`, `poll`, `buttons`, `button_count`, `audio`, `video` + `_wrap_button_row` helper.
   - Target: ~110 lines — leaving ~90 lines of headroom for T5's stubs.

4. **Update `serverless_message.py`** (if needed):
   - The MRO should still work: `ServerlessMessage` → `ServerlessMessageProperties` → `ServerlessMessageMetadata`.
   - Verify no import changes are needed in `serverless_message.py` since it imports `ServerlessMessageProperties` (which now includes metadata via inheritance).

5. **Run `make check`** — must be 100% green.

6. **Verify line counts**: All files under 200 lines with sufficient headroom for T5.

## Production safety constraints (mandatory)

N/A — testing library, no production resources.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: Extracting existing code, not writing new code.
- **Correct file locations**: New file in `tg_auto_test/test_utils/` following `serverless_message_*.py` naming.
- **No regressions**: All existing tests pass unchanged.

## Error handling + correctness rules (mandatory)

- No error handling changes — properties are moved verbatim.
- Do not add any try/catch or fallback behavior.

## Zero legacy tolerance rule (mandatory)

- After extraction, `serverless_message_properties.py` must not contain the moved properties.
- Remove unused imports.
- No duplicate code between files.

## Acceptance criteria (testable)

1. `serverless_message_metadata.py` exists with the extracted metadata properties, identical signatures and behavior.
2. `serverless_message_properties.py` inherits from `ServerlessMessageMetadata` and no longer contains extracted properties.
3. MRO chain: `ServerlessMessage` → `ServerlessMessageProperties` → `ServerlessMessageMetadata`.
4. All files under 200 lines.
5. `serverless_message_properties.py` has at least ~80 lines of headroom (under ~120 lines).
6. `make check` is 100% green.

## Verification / quality gates

- [ ] `make check` passes
- [ ] `wc -l` on all message files shows < 200
- [ ] `serverless_message_properties.py` is under 120 lines
- [ ] No new warnings introduced
- [ ] Existing conformance tests still pass

## Edge cases

- `serverless_message_properties.py` currently has a module-level function `_wrap_button_row` — this must stay with the `buttons` property since it's used only there.
- Properties referencing `self._sender_id`, `self._chat_id_value`, `self.text` — these are defined on `ServerlessMessage` (the concrete dataclass) and available via MRO in the mixin. Verify this works (it does — same pattern as existing code).

## Notes / risks

- **Risk**: `models.py` re-exports `_wrap_button_row` from `serverless_message_helpers.py`, not from `serverless_message_properties.py`. No impact on this refactoring.
  - **Mitigation**: Confirmed — `_wrap_button_row` in `serverless_message_properties.py` is a different function than the one in `serverless_message_helpers.py` (the helpers one is the type alias). The one in properties is the actual implementation. It stays in properties.
