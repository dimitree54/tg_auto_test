---
Task ID: `T2`
Title: `Create interface conformance tests`
Depends on: `--`
Parallelizable: `yes, with T1`
Owner: `Developer`
Status: `planned`
---

## Goal / value

Automated tests exist that verify our public interfaces match real Telethon 1.42's. These tests will initially FAIL for the known divergences, driving the remaining tasks. After T3-T5, all conformance tests must pass.

## Context (contract mapping)

- Requirements: User-provided divergence list (23 items) in sprint request
- Telethon reference: [Telethon 1.42.0 Client docs](https://docs.telethon.dev/en/stable/modules/client.html), [Custom package docs](https://docs.telethon.dev/en/stable/modules/custom.html)

## Preconditions

- Telethon 1.42.x installed (already in `pyproject.toml`: `telethon>=1.42.0,<2`)
- Understanding of `inspect` module for signature comparison

## Non-goals

- Fixing the divergences (that's T3-T5)
- Testing behavioral correctness (only interface shape)
- Covering every Telethon method (only the ones our classes claim to implement)

## Touched surface (expected files / modules)

- New file: `tests/unit/test_telethon_conformance.py` (may need decomposition if >200 lines)
- Possibly: `tests/unit/test_telethon_conformance_client.py`, `tests/unit/test_telethon_conformance_message.py`, `tests/unit/test_telethon_conformance_conversation.py` (if decomposition needed)
- `vulture_whitelist.py` (add new test references if needed)

## Dependencies and sequencing notes

- Independent of T1 (no file overlap)
- Must complete before T3, T4, T5 (they use these tests to validate changes)
- The conformance tests will initially be marked with `pytest.mark.xfail` for known divergences so that `make check` still passes. As T3-T5 fix each divergence, the corresponding `xfail` markers are removed.

## Third-party / library research (mandatory for any external dependency)

- **Library**: Python `inspect` module (stdlib)
  - **Official documentation**: https://docs.python.org/3/library/inspect.html
  - **API reference**: `inspect.signature(obj)` returns `inspect.Signature`; `inspect.Signature.parameters` is `OrderedDict[str, inspect.Parameter]`; `inspect.Parameter.kind` can be `POSITIONAL_ONLY`, `POSITIONAL_OR_KEYWORD`, `KEYWORD_ONLY`, `VAR_POSITIONAL`, `VAR_KEYWORD`; `inspect.Parameter.default` is `inspect.Parameter.empty` when no default.
  - **Usage for this task**: Compare `inspect.signature(our_method).parameters` against `inspect.signature(telethon_method).parameters` for each method we implement.
  - **Known gotchas**: Some Telethon methods may have `*args, **kwargs` wrappers (e.g., `Conversation.send_message(*args, **kwargs)`). Our conformance tests should check parameter names and kinds only for methods with explicit signatures, and skip `*args/**kwargs` pass-throughs.

- **Library**: Telethon 1.42.x
  - **Official documentation**: https://docs.telethon.dev/en/stable/modules/client.html
  - **Conversation class**: https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.conversation.Conversation
  - **Message class**: https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.message.Message
  - **MessageButton class**: https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.messagebutton.MessageButton
  - **Key signatures from docs**:
    - `conversation(entity, *, timeout=60.0, total_timeout=None, max_messages=100, exclusive=True, replies_are_responses=True)` -- on `DialogMethods`
    - `get_messages(entity, limit=None, *, offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, search=None, filter=None, from_user=None, wait_time=None, ids=None, reverse=False, reply_to=None, scheduled=False)` -- on `MessageMethods`
    - `get_me(input_peer=False)` -- on `UserMethods`
    - `get_input_entity(peer)` -- on `UserMethods`
    - `Conversation.get_response(message=None, *, timeout=None)`
    - `Conversation.get_edit(message=None, *, timeout=None)`
    - `Conversation.get_reply(message=None, *, timeout=None)`
    - `Conversation.send_message(*args, **kwargs)` -- pass-through to client
    - `Conversation.send_file(*args, **kwargs)` -- pass-through to client
    - `Message.click(i=None, j=None, *, text=None, filter=None, data=None)` per source code
    - `Message.download_media(file=None, *, thumb=None, progress_callback=None)` per source code
    - `MessageButton.data` property returning `bytes`

## Implementation steps (developer-facing)

1. **Create `tests/unit/test_telethon_conformance.py`** with the following test structure. If the file exceeds ~180 lines, decompose into multiple files (e.g., `_client.py`, `_message.py`, `_conversation.py`).

2. **Client interface tests** -- for each method on `ServerlessTelegramClient` / `ServerlessTelegramClientCore` that has a Telethon equivalent, verify:
   - Method exists on our class
   - Parameter names match (using `inspect.signature`)
   - Parameter kinds match (POSITIONAL_OR_KEYWORD vs KEYWORD_ONLY)
   - Default values match (where applicable: `timeout=60.0` not `10`)
   - Methods tested: `conversation`, `get_messages`, `get_me`, `get_input_entity`, `get_dialogs`, `connect`, `disconnect`

3. **No-extra-public-methods test** -- verify our client classes have no public (non-underscore) methods/properties that don't exist on Telethon's `TelegramClient`, with an explicit allowlist for our additions (if any remain public post-alignment). Currently `_api_calls`, `_last_api_call`, `_pop_response` etc. are already private so they won't flag.

4. **No-extra-public-attributes test** -- verify `ServerlessTelegramClientCore` has no public (non-underscore) instance attributes that don't exist on Telethon's client. This catches `request`, `application`, `chat_id`, `user_id`, `first_name` which should be privatized.

5. **Message interface tests** -- for `ServerlessMessage`, verify:
   - `click()` signature matches Telethon `Message.click(i=None, j=None, *, text=None, filter=None, data=None)`
   - `download_media()` signature matches Telethon `Message.download_media(file=None, *, thumb=None, progress_callback=None)`
   - No extra public (non-underscore) attributes exist that aren't on Telethon's `Message` (catches `poll_data`, `response_file_id`, `reply_markup_data`, `media_photo`, `media_document`, `invoice_data`, `callback_data`)
   - Properties `.photo`, `.document`, `.voice`, `.video_note`, `.file`, `.invoice`, `.poll`, `.buttons`, `.text`, `.id` exist

6. **Button interface tests** -- verify `ServerlessButton` has a `.data` property returning `bytes`, matching `MessageButton.data`.

7. **Conversation interface tests** -- verify:
   - `send_message` exists
   - `send_file` exists
   - `get_response(message=None, *, timeout=None)` signature
   - `get_edit` exists
   - `get_reply` exists

8. **Mark known-failing tests with `pytest.mark.xfail(reason="...")`** so that `make check` passes NOW. Each xfail should reference the specific divergence number (e.g., "Divergence #1: conversation param name").

9. **Run `make check`** to verify all tests pass (xfail tests are expected failures).

## Production safety constraints (mandatory)

N/A -- test-only changes; no runtime code, no database, no shared resources.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: Use stdlib `inspect` module, no new dependencies.
- **Correct file locations**: Tests go in `tests/unit/` following existing convention.
- **No regressions**: All existing tests must continue to pass. New tests use `xfail` for known divergences.
- **File size limit**: If test file exceeds ~180 lines, decompose into multiple files.

## Error handling + correctness rules (mandatory)

- Tests should fail clearly with descriptive assertion messages (e.g., "Parameter 'timeout' should be KEYWORD_ONLY but is POSITIONAL_OR_KEYWORD").
- No silent passes for known issues -- use `xfail` with `strict=True` so tests fail if the divergence is accidentally fixed without removing the marker.

## Zero legacy tolerance rule (mandatory)

- As T3-T5 fix divergences, the corresponding `xfail` markers MUST be removed (not left as "passing xfail"). Using `strict=True` enforces this.

## Acceptance criteria (testable)

1. Test file(s) exist in `tests/unit/` covering client, message, button, and conversation interfaces.
2. Each known divergence (items 1-23 from the divergence list) has at least one test case.
3. All known-divergence tests are marked `xfail(strict=True)` with a reference to the divergence number.
4. Tests for currently-correct interfaces (e.g., `connect`, `disconnect`) pass without xfail.
5. `make check` passes 100%.
6. All files <= 200 lines.

## Verification / quality gates

- [ ] `make check` passes (ruff, pylint 200-line check, vulture, jscpd, pytest)
- [ ] New test files are <= 200 lines each
- [ ] Each divergence from the list has a corresponding test
- [ ] `xfail(strict=True)` used so fixing a divergence without removing the marker causes a test failure

## Edge cases

- Telethon's `Conversation.send_message(*args, **kwargs)` is a pass-through; our test should check method existence only, not parameter-level matching for pass-throughs.
- Some Telethon properties are defined via `__init__` assignment, not `@property`. The conformance test should check both `hasattr` and `inspect` as appropriate.
- `get_dialogs` has many parameters in Telethon; our test should verify the method exists and accepts at minimum the same keyword arguments (or raises NotImplementedError).

## Notes / risks

- **Risk**: Conformance tests may be brittle if Telethon changes signatures in future versions.
  - **Mitigation**: Pin to `telethon>=1.42.0,<2` (already in pyproject.toml). Tests reference specific 1.42 signatures.
- **Risk**: Test file may exceed 200 lines given 23+ divergences to cover.
  - **Mitigation**: Plan decomposition into 2-3 files from the start (client, message, conversation).
