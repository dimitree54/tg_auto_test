---
Task ID: `T2`
Title: `Add send_message, send_file, download_media, get_entity to client`
Depends on: T1
Parallelizable: no (depends on T1 completing to have space in client_core.py)
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Add 4 missing client-level methods to `ServerlessTelegramClientCore` so that the 4 client conformance tests pass. Remove 4 xfail markers.

## Context (contract mapping)

- Requirements: User's requirement "send_message/send_file/download_media — IMPLEMENT (raise if trying to send to non-bot chat)", "get_entity — Raise NotImplementedError"
- Architecture: Single-bot-chat constraint; entity validation for send_message/send_file

## Preconditions

- T1 completed: `serverless_telegram_client_core.py` is well under 200 lines with space for ~60 new lines
- `make check` is green after T1

## Non-goals

- Implementing full Telethon parameter handling — unsupported kwargs raise NotImplementedError
- Demo UI changes (Demo UI uses conversation pattern, not direct client methods)

## Touched surface (expected files / modules)

- `tg_auto_test/test_utils/serverless_telegram_client_core.py` (add 4 methods)
- `tests/unit/test_telethon_conformance_client_extended.py` (remove 4 xfail markers)

## Dependencies and sequencing notes

- Depends on T1 because client_core.py is currently at 200 lines. After T1 extracts ~70 lines, there's room.
- T5 depends on T2 because `message.reply()` delegates to `client.send_message()`.

## Third-party / library research (mandatory for any external dependency)

- **Library/API**: Telethon `TelegramClient` — version installed in project (verified via `uv run python -c "import telethon; print(telethon.__version__)"`)
- **Exact signatures (verified via `inspect.signature()` at runtime)**:

  **`TelegramClient.send_message`**:
  ```
  (entity, message='', *, reply_to=None, attributes=None, parse_mode=(),
   formatting_entities=None, link_preview=True, file=None, thumb=None,
   force_document=False, clear_draft=False, buttons=None, silent=None,
   background=None, supports_streaming=False, schedule=None, comment_to=None,
   nosound_video=None, send_as=None, message_effect_id=None)
  ```
  - `entity`: POSITIONAL_OR_KEYWORD, no default
  - `message`: POSITIONAL_OR_KEYWORD, default=`''`
  - All others: KEYWORD_ONLY with defaults as shown

  **`TelegramClient.send_file`**:
  ```
  (entity, file, *, caption=None, force_document=False, mime_type=None,
   file_size=None, clear_draft=False, progress_callback=None, reply_to=None,
   attributes=None, thumb=None, allow_cache=True, parse_mode=(),
   formatting_entities=None, voice_note=False, video_note=False, buttons=None,
   silent=None, background=None, supports_streaming=False, schedule=None,
   comment_to=None, ttl=None, nosound_video=None, send_as=None,
   message_effect_id=None, **kwargs)
  ```
  - `entity`: POSITIONAL_OR_KEYWORD, no default
  - `file`: POSITIONAL_OR_KEYWORD, no default
  - All keyword args with defaults as shown
  - `**kwargs`: VAR_KEYWORD

  **`TelegramClient.download_media`**:
  ```
  (message, file=None, *, thumb=None, progress_callback=None)
  ```
  - `message`: POSITIONAL_OR_KEYWORD, no default
  - `file`: POSITIONAL_OR_KEYWORD, default=`None`
  - `thumb`, `progress_callback`: KEYWORD_ONLY, default=`None`

  **`TelegramClient.get_entity`**:
  ```
  (entity)
  ```
  - `entity`: POSITIONAL_OR_KEYWORD, no default

## Implementation steps (developer-facing)

1. **Add `send_message` to `ServerlessTelegramClientCore`**:
   ```python
   async def send_message(
       self,
       entity: object,
       message: str = "",
       *,
       reply_to: object = None,
       attributes: object = None,
       parse_mode: object = (),
       formatting_entities: object = None,
       link_preview: bool = True,
       file: object = None,
       thumb: object = None,
       force_document: bool = False,
       clear_draft: bool = False,
       buttons: object = None,
       silent: object = None,
       background: object = None,
       supports_streaming: bool = False,
       schedule: object = None,
       comment_to: object = None,
       nosound_video: object = None,
       send_as: object = None,
       message_effect_id: object = None,
   ) -> ServerlessMessage:
   ```
   - Validate entity matches `self._chat_id` (or is the bot username or similar). If not, raise `NotImplementedError("send_message to entities other than the bot chat is not supported")`.
   - Raise `NotImplementedError` for any non-default kwargs (all kwargs besides `message`).
   - Delegate to `self._process_text_message(message)` for the core case.

2. **Add `send_file` to `ServerlessTelegramClientCore`**:
   ```python
   async def send_file(
       self,
       entity: object,
       file: object,
       *,
       caption: object = None,
       force_document: bool = False,
       mime_type: object = None,
       file_size: object = None,
       clear_draft: bool = False,
       progress_callback: object = None,
       reply_to: object = None,
       attributes: object = None,
       thumb: object = None,
       allow_cache: bool = True,
       parse_mode: object = (),
       formatting_entities: object = None,
       voice_note: bool = False,
       video_note: bool = False,
       buttons: object = None,
       silent: object = None,
       background: object = None,
       supports_streaming: bool = False,
       schedule: object = None,
       comment_to: object = None,
       ttl: object = None,
       nosound_video: object = None,
       send_as: object = None,
       message_effect_id: object = None,
       **kwargs: object,
   ) -> ServerlessMessage:
   ```
   - Validate entity matches bot chat; raise NotImplementedError if not.
   - Delegate to `self._process_file_message(file, caption=caption or "", force_document=force_document, voice_note=voice_note, video_note=video_note)`.
   - Raise NotImplementedError for unsupported parameters that have non-default values.

3. **Add `download_media` to `ServerlessTelegramClientCore`**:
   ```python
   async def download_media(
       self,
       message: object,
       file: object = None,
       *,
       thumb: object = None,
       progress_callback: object = None,
   ) -> bytes | None:
   ```
   - Delegate to `message.download_media(file=file, thumb=thumb, progress_callback=progress_callback)`.
   - If `message` doesn't have `download_media`, raise `NotImplementedError`.

4. **Add `get_entity` to `ServerlessTelegramClientCore`**:
   ```python
   async def get_entity(self, entity: object) -> object:
       raise NotImplementedError("get_entity requires Telegram API lookup and is not supported")
   ```

5. **IMPORTANT — line count management**: The 4 methods above have long signatures. If adding all 4 to `serverless_telegram_client_core.py` pushes it over 200 lines, add `send_message` and `send_file` to the `ServerlessClientPublicAPI` mixin (created in T1) instead, since they are public API methods. Keep `download_media` and `get_entity` (shorter) in `client_core.py`. Either way, ensure both files stay under 200 lines.

6. **Remove xfail markers** from `tests/unit/test_telethon_conformance_client_extended.py`:
   - Remove `@pytest.mark.xfail(strict=True, reason="Divergence: missing send_message method")` from `test_client_send_message_signature`
   - Remove `@pytest.mark.xfail(strict=True, reason="Divergence: missing send_file method")` from `test_client_send_file_signature`
   - Remove `@pytest.mark.xfail(strict=True, reason="Divergence: missing download_media method")` from `test_client_download_media_signature`
   - Remove `@pytest.mark.xfail(strict=True, reason="Divergence: missing get_entity method")` from `test_client_get_entity_signature`
   - Also remove the `import pytest` if it's no longer used in that file.

7. **Run `make check`** — must be 100% green. The 4 previously-xfail client tests must now pass.

## Production safety constraints (mandatory)

N/A — testing library, no production resources.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: `send_message` delegates to existing `_process_text_message`; `send_file` delegates to existing `_process_file_message`; `download_media` delegates to `message.download_media()`.
- **Correct file locations**: methods added to existing file (or mixin from T1).
- **No regressions**: all existing tests pass; 4 new tests transition from xfail to pass.

## Error handling + correctness rules (mandatory)

- Entity validation: if entity doesn't match `self._chat_id`, raise `NotImplementedError` immediately — do not silently ignore.
- Unsupported parameters: raise `NotImplementedError` — do not silently ignore.
- `get_entity`: always raises `NotImplementedError`.

## Zero legacy tolerance rule (mandatory)

- Remove all 4 `@pytest.mark.xfail` decorators from the test file.
- Remove `import pytest` from test file if no longer used.
- No dead code left behind.

## Acceptance criteria (testable)

1. `ServerlessTelegramClientCore` has `send_message`, `send_file`, `download_media`, `get_entity` methods.
2. `send_message` signature has these parameter names in order: `entity, message, reply_to, attributes, parse_mode, formatting_entities, link_preview, file, thumb, force_document, clear_draft, buttons, silent, background, supports_streaming, schedule, comment_to, nosound_video, send_as, message_effect_id`.
3. `send_file` signature has these parameter names in order: `entity, file, caption, force_document, mime_type, file_size, clear_draft, progress_callback, reply_to, attributes, thumb, allow_cache, parse_mode, formatting_entities, voice_note, video_note, buttons, silent, background, supports_streaming, schedule, comment_to, ttl, nosound_video, send_as, message_effect_id, kwargs`.
4. `download_media` signature has: `message, file, thumb, progress_callback`.
5. `get_entity` signature has: `entity`.
6. All 4 conformance tests in `test_telethon_conformance_client_extended.py` pass (no xfail).
7. `get_entity` raises `NotImplementedError`.
8. All files under 200 lines.
9. `make check` is 100% green.

## Verification / quality gates

- [ ] `make check` passes
- [ ] 4 previously-xfail tests now pass
- [ ] `wc -l` on all modified files shows < 200
- [ ] No new warnings introduced

## Edge cases

- `send_message(entity=self._chat_id, message="hello")` should work (happy path).
- `send_message(entity=99999, message="hello")` should raise `NotImplementedError` (wrong entity).
- `download_media(message_without_download_media_method)` should raise `NotImplementedError` or `AttributeError` — choose `NotImplementedError` for consistency.
- `send_file` with `**kwargs` — Telethon's signature has `**kwargs`, our stub must too. Raise `NotImplementedError` if any extra kwargs are passed.

## Notes / risks

- **Risk**: `send_message` and `send_file` have very long signatures (20+ parameters each). Even with just the signatures and a few lines of body, each method is ~25 lines. Total ~100 lines for 4 methods.
  - **Mitigation**: After T1 frees ~70 lines, client_core.py drops to ~130. Adding 100 lines puts it at ~230, which exceeds 200. So `send_message` and `send_file` must go in the mixin file (`serverless_client_public_api.py`) from T1, or a second new file. Plan accordingly — step 5 addresses this.
