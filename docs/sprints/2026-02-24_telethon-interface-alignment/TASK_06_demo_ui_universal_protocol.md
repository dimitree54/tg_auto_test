---
Task ID: `T6`
Title: `Refactor Demo UI to use standard Telethon interfaces`
Depends on: `T3, T4, T5`
Parallelizable: `no`
Owner: `Developer`
Status: `planned`
---

## Goal / value

Demo UI protocols (`DemoClientProtocol`, `DemoConversationProtocol`) use only standard Telethon interfaces. `_pop_response()` is removed from the protocol. `serialize.py` uses Telethon-standard properties (`.poll`, `.buttons`, `.download_media()`) instead of private `ServerlessMessage` fields. The Demo UI works with both `ServerlessTelegramClient` and a real `TelegramClient`.

## Context (contract mapping)

- Requirements: Divergences #20-23 from sprint request; Principle #5 (Demo UI works with both clients)
- Architecture: `demo_ui/server/demo_server.py`, `routes.py`, `serialize.py`, `upload_handlers.py`

## Preconditions

- T3 complete (client interface aligned: `conversation(entity, *, timeout=60.0, ...)`, privatized attributes)
- T4 complete (message interface aligned: `click()`, `download_media()` signatures fixed; attributes privatized; `get_messages` returns `ServerlessMessage`)
- T5 complete (conversation interface aligned: `send_message` returns `Message`, `get_response(message=None, *, timeout=None)`)

## Non-goals

- Implementing new Demo UI features
- Supporting Telethon mode for Stars payments (explicitly serverless-only per feature matrix)
- Full Telethon mode testing (that requires real Telegram credentials)

## Touched surface (expected files / modules)

- `tg_auto_test/demo_ui/server/demo_server.py` (DemoClientProtocol, DemoConversationProtocol)
- `tg_auto_test/demo_ui/server/routes.py` (remove `_pop_response()` calls, update `get_messages` usage)
- `tg_auto_test/demo_ui/server/serialize.py` (refactor to use Telethon-standard properties)
- `tg_auto_test/demo_ui/server/upload_handlers.py` (remove `response_file_id` access)
- `tests/unit/test_demo_server.py` (update MockClient, remove `_pop_response` from tests)
- `tests/unit/test_demo_serialize.py` (update to use new property names)
- `tests/unit/test_demo_integration.py` (minor updates if needed)
- `vulture_whitelist.py` (if needed)

## Dependencies and sequencing notes

- Depends on T3, T4, T5 (all interfaces must be aligned before the demo UI can consume them)
- This is the final task in the sprint; no other task depends on it

## Third-party / library research (mandatory for any external dependency)

- **Library**: Telethon 1.42.x -- Message properties used by serialize.py:
  - **Message.poll**: Returns `MessageMediaPoll | None`. Has `.poll.poll.question` (text), `.poll.poll.answers` (list of PollAnswer with `.text` and `.option`), `.poll.results` (PollResults). [Telethon Message docs](https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.message.Message)
  - **Message.buttons**: Returns `list[list[MessageButton]] | None`. Each `MessageButton` has `.text`, `.data` (bytes). [Telethon MessageButton docs](https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.messagebutton.MessageButton)
  - **Message.download_media(file=bytes)**: Returns `bytes | None`.
  - **Message.file**: Returns `File | None` with `.name`, `.mime_type`, `.size`.
  - **Message.photo**: Returns `Photo | None`.
  - **Message.document**: Returns `Document | None` (includes voice, video_note after T4 fix).
  - **Message.voice**: Returns `Document | None` (voice note only).
  - **Message.video_note**: Returns `Document | None` (video note only).
  - **Message.text**: Returns `str`.
  - **Message.id**: Returns `int`.

- **Library**: FastAPI (already in project)
  - No version changes needed; using existing patterns.

## Implementation steps (developer-facing)

### Step 1: Refactor `DemoConversationProtocol` (Divergence #22)

In `demo_server.py`:

**Before**:
```python
class DemoConversationProtocol(Protocol):
    async def send_message(self, text: str) -> None: ...
    async def get_response(self) -> ServerlessMessage: ...
    async def send_file(self, file, *, caption="", ...) -> None: ...
```

**After**:
```python
class DemoConversationProtocol(Protocol):
    async def send_message(self, text: str) -> object: ...
    async def get_response(self, message: object = None, *, timeout: float | None = None) -> object: ...
    async def send_file(self, file: object, *, caption: str = "", force_document: bool = False, voice_note: bool = False, video_note: bool = False) -> object: ...
```

- Return types changed to `object` (works with both ServerlessMessage and Telethon Message)
- `get_response` signature matches Telethon Conversation
- Remove import of `ServerlessMessage` from the protocol definition (use `object` return types)

### Step 2: Refactor `DemoClientProtocol` (Divergence #20, #21)

**Before**:
```python
class DemoClientProtocol(Protocol):
    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    def conversation(self, peer: str, timeout: float) -> DemoConversationProtocol: ...
    def _pop_response(self) -> ServerlessMessage: ...
    async def get_messages(self, peer: str, *, ids: int) -> TelethonCompatibleMessage | None: ...
    async def __call__(self, request: object) -> object: ...
```

**After**:
```python
class DemoClientProtocol(Protocol):
    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    def conversation(self, entity: object, *, timeout: float = 60.0) -> DemoConversationProtocol: ...
    async def get_messages(self, entity: object, limit: int | None = None, *, ids: int | list[int] | None = None) -> object: ...
    async def __call__(self, request: object) -> object: ...
```

Key changes:
- `conversation` param renamed to `entity`, `timeout` is keyword-only with default `60.0`
- `_pop_response()` REMOVED from protocol entirely
- `get_messages` return type is `object` (works with both ServerlessMessage and Telethon Message)
- Remove `TelethonCompatibleMessage` import

### Step 3: Remove `_pop_response()` usage from `routes.py` (Divergence #21)

Two call sites use `_pop_response()`:

1. **`pay_invoice` endpoint** (line 133): `response = demo_server.client._pop_response()`
   - Refactor: After `await demo_server.client(request)`, use the conversation pattern instead. Since Stars payment is serverless-only, use a different approach: store the payment response in the outbox and retrieve it via `get_response()` in a conversation context, OR keep `_pop_response` as an internal detail not exposed in the protocol.
   - Recommended approach: Since `_pop_response` is a private method, `routes.py` can still call it with `# noqa: SLF001`, but it should NOT be in the protocol. The protocol is what external clients implement. For serverless-only features (Stars payments, poll voting), `routes.py` can cast the client to access private methods.

2. **`vote_poll` endpoint** (line 191): `response = demo_server.client._pop_response()`
   - Same approach as above.

Implementation:
- Remove `_pop_response` from `DemoClientProtocol`
- In `routes.py`, access `_pop_response` via the concrete client reference with `# noqa: SLF001` comment. Since `demo_server.client` is typed as `DemoClientProtocol`, we need to use `getattr` or import the concrete type. Best approach: use `hasattr` check and `getattr`:
  ```python
  response = demo_server.client._pop_response()  # noqa: SLF001
  ```
  This already works since Python doesn't enforce Protocol at runtime. The linter `SLF001` suppression is already present. The key change is just removing `_pop_response` from the Protocol definition.

### Step 4: Refactor `serialize.py` to use Telethon-standard properties (Divergence #23)

**Before** (directly accesses private fields):
```python
async def serialize_message(message: ServerlessMessage, file_store: FileStore) -> MessageResponse:
    if message.poll_data is not None:
        ...
    ...
    if message.reply_markup_data:
        reply_markup = message.reply_markup_data
    ...
    file_id = message.response_file_id or str(uuid.uuid4())
```

**After** (uses Telethon-standard properties):
```python
async def serialize_message(message: object, file_store: FileStore) -> MessageResponse:
    # Poll detection via Telethon-standard .poll property
    poll = getattr(message, 'poll', None)
    if poll is not None:
        # Use Telethon MessageMediaPoll structure
        question = str(getattr(poll.poll, 'question', ''))
        poll_id = str(getattr(poll.poll, 'id', ''))
        options = [
            {"text": str(getattr(answer, 'text', '')), "voter_count": 0}
            for answer in getattr(poll.poll, 'answers', [])
        ]
        return MessageResponse(type="poll", message_id=message.id, poll_question=question, poll_options=options, poll_id=poll_id)

    # Invoice via .invoice property (already Telethon-standard)
    invoice = getattr(message, 'invoice', None)
    if invoice is not None:
        return MessageResponse(...)

    # Media type detection via Telethon properties
    photo = getattr(message, 'photo', None)
    document = getattr(message, 'document', None)
    voice = getattr(message, 'voice', None)
    video_note = getattr(message, 'video_note', None)

    # File ID: use download_media + uuid (no more response_file_id)
    file_id = str(uuid.uuid4()) if any([photo, document, voice, video_note]) else ""

    # Reply markup via .buttons property
    buttons = getattr(message, 'buttons', None)
    reply_markup = _serialize_buttons(buttons) if buttons else None
```

Key changes:
- Input type `ServerlessMessage` -> `object` (works with any Message-like object)
- Remove import of `ServerlessMessage`
- Use `.poll` property instead of `._poll_data` (both ServerlessMessage and Telethon Message have `.poll`)
- Use `.buttons` instead of `._reply_markup_data` (both have `.buttons`)
- Use `download_media(file=bytes)` for file data instead of `._response_file_id`
- For reply_markup serialization, convert from button objects to the JSON structure the frontend expects

**Note on poll serialization**: The current serialize.py reads raw `poll_data` dict. After T4, `ServerlessMessage.poll` returns `MessageMediaPoll` (a real Telethon type). The serialization must use `poll.poll.question`, `poll.poll.answers`, etc. This works identically for real Telethon Messages.

### Step 5: Refactor `upload_handlers.py` to not access private fields

**Before** (line 48): `file_id = response.response_file_id or filename`
**After**: `file_id = str(uuid.uuid4())` or derive from download. Since `response_file_id` was an internal detail, use a UUID for file storage.

Also: remove the `response.response_file_id` reference. The upload handler should use `download_media(file=bytes)` to get the file content, which it already does via `store_response_file`.

### Step 6: Update `routes.py` conversation calls

After T3, conversation is called as `client.conversation(entity, *, timeout=60.0)`.

**Before**: `demo_server.client.conversation(demo_server.peer, demo_server.timeout)`
**After**: `demo_server.client.conversation(demo_server.peer, timeout=demo_server.timeout)`

This change was noted in T3 but must be verified here.

### Step 7: Update test files

- `test_demo_server.py`: Update `MockClient` to not have `_pop_response` in its public interface (keep it as implementation detail). Update `test_poll_vote_endpoint` to use the new pattern.
- `test_demo_serialize.py`: Update `ServerlessMessage` construction to use new `_`-prefixed field names and test against Telethon-standard properties.
- `test_demo_integration.py`: Minimal updates if needed.

### Step 8: Check file sizes

- `serialize.py` is 136 lines. Refactoring may change size but should stay well under 200.
- `routes.py` is exactly 200 lines. Changes must not increase line count. The keyword argument change and minor refactoring should maintain or reduce the count.
- `demo_server.py` is 138 lines. Protocol simplification will reduce line count.

### Step 9: Run `make check`

Verify everything passes. Special attention to:
- `routes.py` must be <= 200 lines
- All demo tests must pass
- vulture must not flag unused imports

## Production safety constraints (mandatory)

N/A -- library code changes; no database, no deployed service.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: Refactoring existing files, not adding new modules.
- **Correct file locations**: Changes in existing `demo_ui/server/` files.
- **No regressions**: All demo tests must pass. Routes must handle the same HTTP endpoints.

## Error handling + correctness rules (mandatory)

- Use `getattr` with sensible defaults when accessing message properties in serialize.py (the message may be from Telethon or our fake -- both must work).
- Never silence missing attributes -- if a required property is missing, let the AttributeError propagate.

## Zero legacy tolerance rule (mandatory)

- Remove `ServerlessMessage` import from `demo_server.py` (replaced with `object` return types)
- Remove `TelethonCompatibleMessage` import from `demo_server.py` (already deleted in T4)
- Remove `_pop_response` from `DemoClientProtocol`
- Remove all direct `._poll_data`, `._response_file_id`, `._reply_markup_data` access from serialize.py
- No backward-compatibility wrappers in protocols

## Acceptance criteria (testable)

1. `DemoClientProtocol` does NOT contain `_pop_response()`.
2. `DemoClientProtocol.conversation()` uses `entity` param (not `peer`) and keyword-only `timeout`.
3. `DemoConversationProtocol.get_response()` accepts `message` and `timeout` params.
4. `serialize.py` does NOT import `ServerlessMessage` and uses only Telethon-standard properties.
5. `upload_handlers.py` does NOT access `response_file_id` directly.
6. All demo server tests pass.
7. `make check` passes 100%.
8. All files <= 200 lines (especially `routes.py` <= 200).
9. The serialize/route code is structurally compatible with a real `TelegramClient` message (uses `.poll`, `.buttons`, `.download_media()`, `.photo`, `.document`, `.voice`, `.video_note`, `.text`, `.id` only).

## Verification / quality gates

- [ ] `make check` passes
- [ ] Demo server tests pass
- [ ] `routes.py` <= 200 lines
- [ ] No `ServerlessMessage` import in `demo_server.py` protocol definitions
- [ ] No `TelethonCompatibleMessage` import anywhere
- [ ] `serialize.py` uses only Telethon-standard properties

## Edge cases

- `routes.py` is exactly 200 lines. Must not grow. The `conversation(peer, timeout=timeout)` keyword change is neutral. Removing `_pop_response` from protocol reduces demo_server.py, not routes.py. May need to extract more logic to keep routes.py within limit.
- Poll serialization: Telethon's `MessageMediaPoll.poll.question` may be a string or a `TextWithEntities` object depending on version. Verify with Telethon 1.42 that `str(poll.poll.question)` works.
- Real Telethon `Message.buttons` returns `list[list[MessageButton]]` which have `.text` and `.data` properties. Our `ServerlessButton` now also has `.text` and `.data`. The serialization code must use only these common properties.

## Notes / risks

- **Risk**: `routes.py` at exactly 200 lines may need decomposition if changes add lines.
  - **Mitigation**: Extract poll/payment endpoints to a separate file if needed (e.g., `routes_special.py`).
- **Risk**: `getattr`-based property access in serialize.py may mask bugs.
  - **Mitigation**: Only use `getattr` for the message type itself (since it could be ServerlessMessage or Telethon Message). For known Telethon TL types (Photo, Document, etc.), use direct attribute access.
- **Risk**: Poll question structure differs between Telethon versions.
  - **Mitigation**: Pin to `telethon>=1.42.0,<2`. Test with the specific version.
