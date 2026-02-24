---
Task ID: `T5`
Title: `Fix ServerlessTelegramConversation public interface`
Depends on: `T2`
Parallelizable: `no`
Owner: `Developer`
Status: `planned`
---

## Goal / value

`ServerlessTelegramConversation` public methods match real Telethon 1.42 `Conversation` class signatures. `send_message()` and `send_file()` return `ServerlessMessage` (matching Telethon returning `Message`). `get_response()` accepts `message` and `timeout` params. `get_reply()` and `get_edit()` stubs exist and raise `NotImplementedError`.

## Context (contract mapping)

- Requirements: Divergences #7-10 from sprint request
- Telethon reference: [Conversation class](https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.conversation.Conversation)

## Preconditions

- T2 complete (conformance tests exist)
- T4 complete (ServerlessMessage is the return type for `send_message`/`send_file`, and `_pop_response` returns it)

## Non-goals

- Implementing full Telethon conversation behavior (timeouts, message tracking, etc.)
- Fixing demo UI protocols (T6)
- Adding `wait_event`, `mark_read`, `cancel`, `cancel_all` (not currently needed; can be added as NotImplementedError stubs if conformance tests require them)

## Touched surface (expected files / modules)

- `tg_auto_test/test_utils/serverless_telegram_conversation.py` (primary)
- `tests/unit/test_serverless_client_text.py` (may need updates if return type assertions added)
- `tests/unit/test_serverless_client_media.py` (same)
- `tests/unit/test_telethon_conformance*.py` (remove xfail markers)
- `vulture_whitelist.py` (add `get_reply`, `get_edit` if vulture flags them)

## Dependencies and sequencing notes

- Depends on T2 (conformance tests)
- Should run after T4 (needs ServerlessMessage as return type)
- Must complete before T6 (demo UI depends on aligned conversation interface)
- Minimal file overlap with T3/T4 (conversation.py is mostly standalone)

## Third-party / library research (mandatory for any external dependency)

- **Library**: Telethon 1.42.x
  - **Conversation.send_message**: `send_message(*args, **kwargs)` -- pass-through to `client.send_message(entity, *args, **kwargs)`. Returns `Message`. [Conversation docs](https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.conversation.Conversation.send_message)
  - **Conversation.send_file**: `send_file(*args, **kwargs)` -- pass-through to `client.send_file(entity, *args, **kwargs)`. Returns `Message`. [Conversation docs](https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.conversation.Conversation.send_file)
  - **Conversation.get_response**: `get_response(message=None, *, timeout=None)` -- returns `Message`. [Conversation docs](https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.conversation.Conversation.get_response)
  - **Conversation.get_reply**: `get_reply(message=None, *, timeout=None)` -- returns `Message`. [Conversation docs](https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.conversation.Conversation.get_reply)
  - **Conversation.get_edit**: `get_edit(message=None, *, timeout=None)` -- returns `Message`. [Conversation docs](https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.conversation.Conversation.get_edit)
  - **Note**: Telethon's `send_message` and `send_file` use `*args, **kwargs` pass-through pattern. Our implementation has explicit params, which is acceptable since our signatures are a subset of Telethon's.

## Implementation steps (developer-facing)

### Step 1: Fix `send_message()` return type (Divergence #7)

In `serverless_telegram_conversation.py`:

**Before**:
```python
async def send_message(self, text: str) -> None:
    await self._client._process_text_message(text)
```

**After**:
```python
async def send_message(self, text: str) -> ServerlessMessage:
    return await self._client._process_text_message(text)
```

The `_process_text_message` already returns `ServerlessMessage` (see `serverless_telegram_client_core.py` line 104-113). We just need to capture and return it.

### Step 2: Fix `send_file()` return type (Divergence #8)

**Before**:
```python
async def send_file(self, file, *, caption="", force_document=False, voice_note=False, video_note=False) -> None:
    await self._client._process_file_message(...)
```

**After**:
```python
async def send_file(self, file, *, caption="", force_document=False, voice_note=False, video_note=False) -> ServerlessMessage:
    return await self._client._process_file_message(...)
```

### Step 3: Fix `get_response()` signature (Divergence #9)

**Before**:
```python
async def get_response(self) -> ServerlessMessage:
    return self._client._pop_response()
```

**After**:
```python
async def get_response(self, message: object = None, *, timeout: float | None = None) -> ServerlessMessage:
    if message is not None:
        raise NotImplementedError("message parameter not supported in serverless mode")
    if timeout is not None:
        raise NotImplementedError("timeout parameter not supported in serverless mode")
    return self._client._pop_response()
```

### Step 4: Add `get_reply()` stub (Divergence #10)

```python
async def get_reply(self, message: object = None, *, timeout: float | None = None) -> ServerlessMessage:
    raise NotImplementedError("get_reply() not supported in serverless mode")
```

### Step 5: Add `get_edit()` stub (Divergence #10)

```python
async def get_edit(self, message: object = None, *, timeout: float | None = None) -> ServerlessMessage:
    raise NotImplementedError("get_edit() not supported in serverless mode")
```

### Step 6: Update ConversationClient protocol

The `ConversationClient` protocol in the same file currently declares `_process_text_message` returning `ServerlessMessage` and `_process_file_message` returning `ServerlessMessage`. These are already correct for the new return-value behavior. No changes needed to the protocol.

### Step 7: Check file size

`serverless_telegram_conversation.py` is currently 62 lines. Adding `get_reply`, `get_edit`, and expanding `get_response` adds ~15 lines. Total ~77 lines -- well within 200-line limit.

### Step 8: Update vulture_whitelist.py

Add `get_reply` and `get_edit` to the vulture whitelist since they're stubs that raise NotImplementedError and may not be directly called in tests (though conformance tests should reference them).

### Step 9: Update existing tests (if needed)

Existing tests call `await conv.send_message("hello")` and discard the return value. Since the return type changed from `None` to `ServerlessMessage`, existing tests still work -- they just ignore the return value.

No existing test calls `conv.get_response(message=..., timeout=...)`, so no test updates needed.

### Step 10: Remove xfail markers from conformance tests

For divergences #7-10, remove `pytest.mark.xfail` markers in the conformance test files.

### Step 11: Run `make check`

Verify all passes.

## Production safety constraints (mandatory)

N/A -- library code changes; no database, no deployed service.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: Modifying existing file only.
- **Correct file locations**: Changes in existing `serverless_telegram_conversation.py`.
- **No regressions**: Return type change from None to ServerlessMessage is backward compatible (callers that ignore the return value are unaffected).

## Error handling + correctness rules (mandatory)

- `get_response(message=X)` with non-None message raises `NotImplementedError` -- not silently ignored.
- `get_response(timeout=X)` with non-None timeout raises `NotImplementedError`.
- `get_reply()` raises `NotImplementedError` always.
- `get_edit()` raises `NotImplementedError` always.

## Zero legacy tolerance rule (mandatory)

- Old `-> None` return types removed; `-> ServerlessMessage` is the only return type.
- No backward-compatibility wrappers.

## Acceptance criteria (testable)

1. `send_message()` returns `ServerlessMessage`.
2. `send_file()` returns `ServerlessMessage`.
3. `get_response(message=None, *, timeout=None)` signature matches Telethon.
4. `get_reply()` exists and raises `NotImplementedError`.
5. `get_edit()` exists and raises `NotImplementedError`.
6. All conformance tests for conversation pass (xfail removed).
7. All existing tests pass (no regressions from return type change).
8. `make check` passes 100%.
9. File <= 200 lines (~77 lines expected).

## Verification / quality gates

- [ ] `make check` passes
- [ ] Conversation conformance tests pass (no xfail)
- [ ] File <= 200 lines
- [ ] `get_reply()` and `get_edit()` raise NotImplementedError

## Edge cases

- Tests that do `await conv.send_message("hello")` without capturing the return value: Python allows ignoring return values; no breakage.
- `DemoConversationProtocol` in `demo_server.py` declares `send_message -> None` and `get_response() -> ServerlessMessage`. These will need updating in T6, but T5 changes the implementation, not the protocol. The protocol is structurally typed, so as long as the implementation is compatible with what callers expect, it works.

## Notes / risks

- **Risk**: Changing return types from None to ServerlessMessage might seem backward-incompatible, but no caller checks `is None` on these returns.
  - **Mitigation**: Verified by reading all test files -- no test asserts `conv.send_message(...) is None`.
- **Risk**: Adding params to `get_response` that raise NotImplementedError might surprise users.
  - **Mitigation**: This matches the sprint contract: "unimplemented features raise NotImplementedError."
