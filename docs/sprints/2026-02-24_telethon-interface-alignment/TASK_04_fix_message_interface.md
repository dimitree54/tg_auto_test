---
Task ID: `T4`
Title: `Fix ServerlessMessage and ServerlessButton public interface; eliminate TelethonCompatibleMessage`
Depends on: `T2`
Parallelizable: `no`
Owner: `Developer`
Status: `planned`
---

## Goal / value

`ServerlessMessage` public properties/methods match real Telethon 1.42 `Message` exactly. `ServerlessButton` exposes `.data` as `bytes` matching `MessageButton`. `TelethonCompatibleMessage` is deleted; `get_messages()` returns `ServerlessMessage` directly. Non-Telethon public attributes on `ServerlessMessage` are privatized.

## Context (contract mapping)

- Requirements: Divergences #11-19 from sprint request
- Telethon reference: [Message class](https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.message.Message), [MessageButton class](https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.messagebutton.MessageButton)

## Preconditions

- T2 complete (conformance tests exist)
- T3 complete (client attributes privatized -- `self._request` is now available for `get_messages` changes)

## Non-goals

- Fixing conversation interface (T5)
- Fixing demo UI protocols (T6)
- Adding full Telethon Message properties beyond what's needed for our test use cases (stubs with NotImplementedError are fine)

## Touched surface (expected files / modules)

- `tg_auto_test/test_utils/models.py` (primary -- ServerlessMessage, ServerlessButton)
- `tg_auto_test/test_utils/telethon_compatible_message.py` (DELETE this file)
- `tg_auto_test/test_utils/serverless_telegram_client_core.py` (update `get_messages` to return ServerlessMessage)
- `tg_auto_test/test_utils/serverless_update_processor.py` (may reference public attrs)
- `tg_auto_test/test_utils/response_processor.py` (builds ServerlessMessage -- may set public attrs)
- `tg_auto_test/test_utils/message_factory.py` (builds ServerlessMessage)
- `tg_auto_test/test_utils/message_factory_media.py` (builds ServerlessMessage)
- `tg_auto_test/test_utils/message_factory_invoice.py` (builds ServerlessMessage)
- `tg_auto_test/test_utils/message_factory_poll.py` (builds ServerlessMessage)
- `tg_auto_test/demo_ui/server/demo_server.py` (imports TelethonCompatibleMessage -- update)
- `tg_auto_test/demo_ui/server/serialize.py` (reads `poll_data`, `response_file_id`, `reply_markup_data`)
- `tg_auto_test/demo_ui/server/upload_handlers.py` (reads `response_file_id`)
- `tg_auto_test/demo_ui/server/routes.py` (uses get_messages return type)
- `tests/unit/test_serverless_client_callbacks.py` (imports TelethonCompatibleMessage)
- `tests/unit/test_demo_server.py` (creates ServerlessMessage with public attrs)
- `tests/unit/test_demo_serialize.py` (creates ServerlessMessage with public attrs)
- `tests/unit/test_telethon_conformance*.py` (remove xfail markers)
- `vulture_whitelist.py`

## Dependencies and sequencing notes

- Depends on T2 (conformance tests) and should run after T3 (client privatized)
- Must complete before T6 (demo UI depends on aligned message interface)
- `models.py` is 186 lines; adding stubs will push it over 200. MUST decompose.

## Third-party / library research (mandatory for any external dependency)

- **Library**: Telethon 1.42.x
  - **Message.click**: From Telethon source: `async def click(self, i=None, j=None, *, text=None, filter=None, data=None)`. Returns `Message` or result. [Message docs](https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.message.Message)
  - **Message.download_media**: From Telethon source: `async def download_media(self, file=None, *, thumb=None, progress_callback=None)`. `file` can be `str`, `bytes`, `BinaryIO`, etc. When `file=bytes`, returns raw bytes. [DownloadMethods](https://docs.telethon.dev/en/stable/modules/client.html#telethon.client.downloads.DownloadMethods.download_media)
  - **Message.document**: Returns `Document` for ANY document type including voice and video_note. The `.voice` and `.video_note` properties are separate convenience accessors. [Message docs](https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.message.Message)
  - **MessageButton.data**: Property that returns `bytes` -- the callback data. [MessageButton docs](https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.messagebutton.MessageButton)

## Implementation steps (developer-facing)

### Step 1: Decompose `models.py` BEFORE making changes

`models.py` is 186 lines and will exceed 200 with additions. Extract `ServerlessMessage` into a new file FIRST:

- Create `tg_auto_test/test_utils/serverless_message.py` containing the `ServerlessMessage` class, `_wrap_button_row`, `ReplyMarkup`, and `ClickCallback` type aliases
- Create `tg_auto_test/test_utils/serverless_button.py` containing `ServerlessButton`
- Keep `models.py` as a re-export hub: import and re-export all public symbols from the new files plus `FileData` and `TelegramApiCall` (which stay in models.py)
- Verify no circular imports
- Run `make check` to confirm decomposition is clean

### Step 2: Privatize ServerlessMessage public attributes (Divergence #15, #16)

In the new `serverless_message.py`:

Rename dataclass fields:
- `media_photo` -> `_media_photo`
- `media_document` -> `_media_document`
- `invoice_data` -> `_invoice_data`
- `poll_data` -> `_poll_data`
- `response_file_id` -> `_response_file_id`
- `reply_markup_data` -> `_reply_markup_data`

Update all internal references:
- `self.media_photo` -> `self._media_photo` in property methods
- `self.media_document` -> `self._media_document`
- `self.invoice_data` -> `self._invoice_data`
- `self.poll_data` -> `self._poll_data`
- `self.response_file_id` -> `self._response_file_id`
- `self.reply_markup_data` -> `self._reply_markup_data`

Update all external references in:
- `response_processor.py`, `message_factory*.py` -- where `ServerlessMessage(media_photo=..., poll_data=..., ...)` is constructed. These files must use the new `_`-prefixed field names. Since these are internal test infrastructure, `# noqa: SLF001` is appropriate if the linter complains about accessing private attrs from outside, but dataclass field names with `_` prefix are set at construction so this should be fine.
- `serialize.py` -- reads `message.poll_data`, `message.response_file_id`, `message.reply_markup_data`. These must be updated to `message._poll_data`, etc. (interim; T6 will refactor to use Telethon-standard APIs instead).
- `upload_handlers.py` -- reads `response.response_file_id`. Update to `response._response_file_id`.
- Test files -- `test_demo_serialize.py` constructs `ServerlessMessage(poll_data=..., reply_markup_data=..., invoice_data=..., response_file_id=..., media_document=...)`. Update to use `_`-prefixed names.

### Step 3: Fix `.document` property (Divergence #14)

In Telethon, `.document` returns the `Document` object even for voice/video_note. Our implementation filters them out. Fix:

**Before** (filters voice/video_note):
```python
@property
def document(self) -> Document | None:
    if self._media_document is None:
        return None
    for attr in self._media_document.attributes:
        if isinstance(attr, DocumentAttributeAudio) and attr.voice:
            return None
        if isinstance(attr, DocumentAttributeVideo) and attr.round_message:
            return None
    return self._media_document
```

**After** (matches Telethon -- returns Document for all document types):
```python
@property
def document(self) -> Document | None:
    return self._media_document
```

**Test impact**: `test_serverless_client_media.py` line 39 asserts `msg.document is None` for photo echo (this should still pass since photos have `_media_photo`, not `_media_document`). Line 119 asserts `photo_msg.document is None` -- same, still passes. Line 64 asserts `msg.document is not None` for forced document -- still passes. No test asserts `msg.document is None` when `voice` or `video_note` is set, so this behavioral change should NOT break existing tests.

### Step 4: Fix `click()` signature (Divergence #12)

**Before**: `async def click(self, *, data: bytes) -> "ServerlessMessage"`
**After**: `async def click(self, i: int | None = None, j: int | None = None, *, text: str | None = None, filter: object = None, data: bytes | None = None) -> "ServerlessMessage"`

- `i`, `j`, `text`, `filter` raise `NotImplementedError` if passed with non-None values
- `data` is now optional (None by default); raise `ValueError("At least one of i, j, text, filter, or data must be provided")` if all are None

### Step 5: Fix `download_media()` signature (Divergence #13)

**Before**: `async def download_media(self, file: type = bytes) -> bytes | None`
**After**: `async def download_media(self, file: object = None, *, thumb: object = None, progress_callback: object = None) -> bytes | None`

- `file=None` now means same as `file=bytes` for backward compat (download to memory)
- If `file` is not `None` and not `bytes`, raise `NotImplementedError`
- If `thumb` or `progress_callback` are not None, raise `NotImplementedError`

### Step 6: Add `.data` property to ServerlessButton (Divergence #17)

In `serverless_button.py`:

```python
@property
def data(self) -> bytes:
    return self.callback_data.encode()
```

Keep `callback_data` as `_callback_data` (privatize the str field) and keep the public `.data` property returning `bytes`.

Actually, since `callback_data` is used in existing tests (e.g., `btn_a.callback_data.encode()`), we have a choice:
- Privatize `callback_data` to `_callback_data` and add `.data` -> `bytes` as the public API
- This breaks the test at line 126: `btn_a.callback_data.encode()`. Change to `btn_a.data`.

### Step 7: Eliminate TelethonCompatibleMessage (Divergence #18, #19)

- Delete `tg_auto_test/test_utils/telethon_compatible_message.py`
- In `serverless_telegram_client_core.py`, update `get_messages()` to return `ServerlessMessage` instead of `TelethonCompatibleMessage`:
  - Create a `ServerlessMessage` with `id=msg_id` and `_click_callback=self._handle_click`
  - Return type: `ServerlessMessage | list[ServerlessMessage] | None`
- Remove the import of `TelethonCompatibleMessage` from `serverless_telegram_client_core.py`
- Update `demo_server.py` to remove the import of `TelethonCompatibleMessage`
- Update `DemoClientProtocol.get_messages` return type
- Update `test_serverless_client_callbacks.py`: remove `TelethonCompatibleMessage` import, remove `cast(TelethonCompatibleMessage, message)` -- just use the message directly
- Remove `TelethonCompatibleMessage` from `vulture_whitelist.py` if present

### Step 8: Update vulture_whitelist.py

- Remove entries for deleted/renamed symbols
- Add entries for new symbols if vulture flags them (e.g., `data` property on ServerlessButton)

### Step 9: Remove xfail markers from conformance tests

For divergences #11-19 in the conformance tests, remove `pytest.mark.xfail` markers.

### Step 10: Run `make check`

Verify all passes. Pay special attention to:
- 200-line limit on new `serverless_message.py`
- No unused imports after removing TelethonCompatibleMessage
- vulture doesn't flag new private attributes

## Production safety constraints (mandatory)

N/A -- library code changes; no database, no deployed service.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: Decomposing existing file, not adding new functionality.
- **Correct file locations**: New files follow existing `test_utils/` convention.
- **No regressions**: All existing tests must pass after updates. The `.document` behavioral change has been verified not to break existing tests.
- **File size limit**: Decompose `models.py` FIRST before adding anything.

## Error handling + correctness rules (mandatory)

- `click()` with all params None raises `ValueError` (fail-fast)
- `download_media()` with unsupported `file` type raises `NotImplementedError`
- Unsupported params (`thumb`, `progress_callback`, `i`, `j`, `text`, `filter`) raise `NotImplementedError`

## Zero legacy tolerance rule (mandatory)

- `TelethonCompatibleMessage` class and file deleted entirely
- Old public attribute names on `ServerlessMessage` completely privatized
- Old `callback_data` str field on `ServerlessButton` privatized; `.data` (bytes) is the public API
- No backward-compatibility aliases or wrappers

## Acceptance criteria (testable)

1. `ServerlessMessage.click()` signature matches Telethon: `click(i=None, j=None, *, text=None, filter=None, data=None)`.
2. `ServerlessMessage.download_media()` signature matches Telethon: `download_media(file=None, *, thumb=None, progress_callback=None)`.
3. `ServerlessMessage.document` returns `Document` even for voice/video_note.
4. `ServerlessButton` has `.data` property returning `bytes`.
5. No public attributes `poll_data`, `response_file_id`, `reply_markup_data`, `media_photo`, `media_document`, `invoice_data` on `ServerlessMessage`.
6. `TelethonCompatibleMessage` file does not exist.
7. `get_messages()` returns `ServerlessMessage` (not `TelethonCompatibleMessage`).
8. All conformance tests for message/button pass (xfail removed).
9. All existing tests pass.
10. `make check` passes 100%.
11. All files <= 200 lines.

## Verification / quality gates

- [ ] `make check` passes
- [ ] `telethon_compatible_message.py` does not exist
- [ ] Message/button conformance tests pass (no xfail)
- [ ] All files <= 200 lines
- [ ] `models.py` decomposed cleanly

## Edge cases

- `ServerlessMessage` is a dataclass with `slots=True`. Renaming fields to `_`-prefixed works with dataclasses, but the `__init__` parameter names will also be `_`-prefixed. Callers constructing `ServerlessMessage(_media_photo=..., _poll_data=...)` is valid Python.
- `frozen=False` (it's `slots=True` but NOT `frozen=True` for `ServerlessMessage`) -- check this. Actually it IS `slots=True` without frozen, so field assignment after creation works.
- Removing the voice/video_note filter from `.document` means tests that assert `msg.document is None` for voice messages would break. Check: no existing test does this. The `test_serverless_client_media.py` only tests `msg.voice is not None` for voice, never `msg.document is None` for voice.

## Notes / risks

- **Risk**: Decomposing `models.py` may cause circular imports.
  - **Mitigation**: `serverless_message.py` and `serverless_button.py` only import from `telethon` and `model_helpers.py` -- no circular risk.
- **Risk**: Privatizing dataclass fields may confuse IDE autocompletion for internal constructors.
  - **Mitigation**: Internal code already uses `# noqa: SLF001` pattern extensively. The field names are implementation details.
