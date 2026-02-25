---
Task ID: `T5`
Title: `Add ~32 missing message method/property stubs`
Depends on: T3
Parallelizable: yes, with T4 and T6
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Add `NotImplementedError`-raising stubs for all ~32 missing Telethon `Message` methods and properties identified by T1's reverse conformance tests. After this task, the reverse conformance test for the message class passes (all xfail markers removed for message members).

## Context (contract mapping)

- Requirements: User's GAP 2 — ~32 missing message methods/properties
- Architecture: Stubs distributed across mixin files created/decomposed in T3, each under 200 lines

## Preconditions

- T3 complete (message properties decomposed with headroom)
- T1's reverse conformance test output provides the authoritative list
- `make check` is green

## Non-goals

- Implementing real behavior for any stub
- Modifying existing working properties/methods

## Touched surface (expected files / modules)

- `tg_auto_test/test_utils/serverless_message_serial_stubs.py` (NEW — TL serialization stubs)
- `tg_auto_test/test_utils/serverless_message_metadata.py` (MODIFY — add metadata property stubs if headroom allows)
- `tg_auto_test/test_utils/serverless_message_properties.py` (MODIFY — add remaining property stubs if headroom allows)
- `tg_auto_test/test_utils/serverless_message.py` (MODIFY — add method stubs if headroom allows, or update MRO)
- `tests/unit/test_telethon_reverse_conformance_message.py` (MODIFY — remove xfail markers)

## Dependencies and sequencing notes

- Depends on T3 (message file decomposition must be done first).
- Can run in parallel with T4 (client stubs) and T6 (conversation/button stubs).
- Uses T1's test output as the authoritative list of missing members.

## Third-party / library research

- **Library**: Telethon 1.42.x
- **Message reference**: https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.message.Message
- **Key inheritance**: Telethon's `Message` inherits from `ChatGetter`, `SenderGetter`, and implicitly from TLObject via the generated `telethon.tl.types.Message`. This means many "public" attributes come from:
  - `ChatGetter`: `chat`, `input_chat`, `get_chat`, `get_input_chat`, `chat_id`, `is_private`, `is_group`, `is_channel`
  - `SenderGetter`: `sender`, `input_sender`, `get_sender`, `get_input_sender`, `sender_id`
  - TLObject: `CONSTRUCTOR_ID`, `SUBCLASS_OF_ID`, `from_reader`, `serialize_bytes`, `serialize_datetime`, `to_dict`, `to_json`, `stringify`, `pretty_format`
- **Audit list** (from user, to be confirmed by T1):
  - Properties: `CONSTRUCTOR_ID`, `SUBCLASS_OF_ID`, `action_entities`, `client`, `geo`, `input_chat`, `input_sender`, `is_channel`, `is_group`, `is_private`, `is_reply`, `reply_to_chat`, `reply_to_sender`, `to_id`, `via_input_bot`
  - Methods: `from_reader`, `get_buttons`, `get_chat`, `get_entities_text`, `get_input_chat`, `get_input_sender`, `get_sender`, `mark_read`, `pin`, `pretty_format`, `respond`, `serialize_bytes`, `serialize_datetime`, `stringify`, `to_dict`, `to_json`, `unpin`

## Implementation steps (developer-facing)

1. **Run T1's message reverse conformance test** to get the exact list:
   ```
   uv run pytest tests/unit/test_telethon_reverse_conformance_message.py -v 2>&1 | grep XFAIL
   ```

2. **Group the missing members** into logical locations:

   **`serverless_message_serial_stubs.py`** (NEW, ~60 lines) — TL serialization protocol stubs:
   - Class-level: `CONSTRUCTOR_ID`, `SUBCLASS_OF_ID` (class attributes, set to `0` or raise `NotImplementedError` as `@property`)
   - Methods: `from_reader` (classmethod), `serialize_bytes` (staticmethod), `serialize_datetime` (staticmethod)
   - Methods: `to_dict`, `to_json`, `stringify`, `pretty_format`

   **`serverless_message_metadata.py`** (existing from T3, add stubs ~30 lines) — metadata property stubs:
   - `client`, `input_chat`, `input_sender`, `is_channel`, `is_group`, `is_private`, `is_reply`
   - `action_entities`, `geo`, `reply_to_chat`, `reply_to_sender`, `to_id`, `via_input_bot`

   **`serverless_message.py`** (existing, add method stubs ~30 lines):
   - `get_buttons`, `get_chat`, `get_entities_text`, `get_input_chat`, `get_input_sender`, `get_sender`
   - `mark_read`, `pin`, `respond`, `unpin`

3. **Create `serverless_message_serial_stubs.py`**:
   - Define class `ServerlessMessageSerialStubs` (mixin).
   - Add TL serialization stubs. These are unusual — `CONSTRUCTOR_ID` and `SUBCLASS_OF_ID` are typically class-level integers in Telethon. To satisfy `hasattr`, define them as class attributes set to `0` (or as `@property` raising `NotImplementedError`). Check what Telethon actually does and match the type.
   - `from_reader` is a classmethod in Telethon. Stub: `@classmethod def from_reader(cls, *args, **kwargs): raise NotImplementedError(...)`.
   - `serialize_bytes` and `serialize_datetime` are staticmethods. Stub as staticmethods.
   - `to_dict`, `to_json`, `stringify`, `pretty_format` are instance methods.

4. **Add metadata stubs to `serverless_message_metadata.py`**:
   - Each missing property: `@property\ndef prop_name(self): raise NotImplementedError("prop_name is not supported in serverless testing mode")`

5. **Add method stubs to `serverless_message.py`**:
   - Each missing method: `async def method_name(self, *args, **kwargs): raise NotImplementedError(...)`
   - Check Telethon source for sync vs async on each method.

6. **Chain the mixin inheritance**:
   - `ServerlessMessageMetadata` inherits from `ServerlessMessageSerialStubs`.
   - Or `ServerlessMessageProperties` inherits from both `ServerlessMessageMetadata` and `ServerlessMessageSerialStubs`.
   - Choose whichever keeps the MRO clean.

7. **Update `tests/unit/test_telethon_reverse_conformance_message.py`**:
   - Remove all xfail markers for message members.
   - Verify allowlist is accurate.

8. **Run `make check`** — must be 100% green.

9. **Verify line counts**: Every file under 200 lines.

## Production safety constraints (mandatory)

N/A — testing library, no production resources.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: Adding stubs to existing mixin architecture from T3.
- **Correct file locations**: Files in `tg_auto_test/test_utils/` with `serverless_message_*` naming.
- **No regressions**: Existing tests pass; only xfail markers removed.

## Error handling + correctness rules (mandatory)

- Every stub raises `NotImplementedError` with a descriptive message.
- No silent fallbacks or empty returns.

## Zero legacy tolerance rule (mandatory)

- All xfail markers for message members removed from reverse conformance test.
- No dead code.

## Acceptance criteria (testable)

1. All ~32 missing message methods/properties exist on `ServerlessMessage` (via MRO).
2. Each stub raises `NotImplementedError` when called/accessed.
3. Reverse conformance test for message passes with no xfail markers for message members.
4. Every file under 200 lines.
5. `make check` is 100% green.

## Verification / quality gates

- [ ] `make check` passes
- [ ] `uv run pytest tests/unit/test_telethon_reverse_conformance_message.py -v` — all tests pass (no xfail)
- [ ] `wc -l` on all message files shows < 200
- [ ] No new warnings introduced

## Edge cases

- `CONSTRUCTOR_ID` and `SUBCLASS_OF_ID` are class-level integer constants in Telethon's generated TL types (e.g., `Message.CONSTRUCTOR_ID = 0x38116ee0`). For `hasattr` to work, these need to be class attributes. Set them to `0` or a sentinel. They are NOT properties — they are plain class attributes.
- `from_reader` is a classmethod. Use `@classmethod`.
- `serialize_bytes` and `serialize_datetime` are staticmethods. Use `@staticmethod`.
- `ServerlessMessage` is a `@dataclass(slots=True)` — adding properties to the mixin works fine (properties are class-level, not instance-level). But class attributes like `CONSTRUCTOR_ID` cannot be added directly to a slots dataclass — they must be on a parent class (mixin). Verify this with the serial stubs mixin.

## Notes / risks

- **Risk**: `@dataclass(slots=True)` and class attributes on mixin — slots dataclass prevents adding class attributes directly, but inherited class attributes from a non-slots parent are fine.
  - **Mitigation**: `ServerlessMessageSerialStubs` (the mixin) is NOT a dataclass, so it can have class attributes. `ServerlessMessage` inherits them through MRO.
- **Risk**: jscpd may flag similar stub patterns across files.
  - **Mitigation**: Each stub has a unique name and message. If jscpd flags, adjust messages.
