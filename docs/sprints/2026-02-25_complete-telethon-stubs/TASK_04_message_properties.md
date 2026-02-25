---
Task ID: `T4`
Title: `Add 19 Telethon-standard message properties to ServerlessMessage`
Depends on: T3
Parallelizable: no (needs T3 to free space)
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Add all message properties required by the `test_message_additional_properties` conformance test. Remove 1 xfail marker. After this task, `ServerlessMessage` exposes the same property surface as Telethon's `Message` for all properties checked by the test.

## Context (contract mapping)

- Requirements: User's requirement to "sync with Telethon interface" for message properties
- Architecture: Properties within single-bot-chat scope return meaningful values; properties requiring entity resolution raise `NotImplementedError` or return `None`

## Preconditions

- T3 completed: `serverless_message.py` is well under 200 lines (~100 lines)
- `make check` is green after T3

## Non-goals

- Message methods (`delete`, `edit`, `reply`, `forward_to`, `get_reply_message`) — that's T5
- Making properties return real Telethon entity objects — out of scope per user guidance

## Touched surface (expected files / modules)

- `tg_auto_test/test_utils/serverless_message.py` (add new dataclass fields and properties) OR
- `tg_auto_test/test_utils/serverless_message_properties.py` (add properties to the mixin from T3)
- `tests/unit/test_telethon_conformance_message_extended.py` (remove 1 xfail marker)
- `vulture_whitelist.py` (may need additions — defer to T7 if possible)

## Dependencies and sequencing notes

- Depends on T3 to free space in `serverless_message.py`.
- Properties will be added to either `serverless_message.py` (if there's room for all) or split between `serverless_message.py` (fields) and `serverless_message_properties.py` (property methods).
- T5 depends on T4 (some methods like `reply` may reference these new fields like `reply_to_msg_id`).

## Third-party / library research (mandatory for any external dependency)

- **Library**: Telethon `Message` class
- **Properties verified via `hasattr(Message, prop)` at runtime**:

  The conformance test checks these properties and only asserts the ones that `hasattr(Message, prop)` returns True:

  | Property | On Telethon Message? | Our implementation |
  |---|---|---|
  | `sender` | Yes | `raise NotImplementedError` (entity resolution) |
  | `sender_id` | Yes | Return `self._sender_id` field (int or None) |
  | `chat` | Yes | `raise NotImplementedError` (entity resolution) |
  | `chat_id` | Yes | Return `self._chat_id` field (int or None) |
  | `date` | **No** | Skip — test won't check |
  | `raw_text` | Yes | Return `self.text` (same for our purposes) |
  | `reply_to_msg_id` | Yes | Return `None` (default; no reply tracking yet) |
  | `forward` | Yes | Return `None` (forwarding not supported) |
  | `via_bot` | Yes | Return `None` (via_bot not supported) |
  | `media` | **No** | Skip — test won't check |
  | `sticker` | Yes | Return `None` (stickers not supported) |
  | `contact` | Yes | Return `None` (contacts not supported) |
  | `location` | **No** | Skip — test won't check |
  | `venue` | Yes | Return `None` (venues not supported) |
  | `audio` | Yes | Derive from `_media_document` (check for AudioAttribute without voice flag) |
  | `voice` | Yes | Already exists — verify it's present |
  | `video` | Yes | Derive from `_media_document` (check for VideoAttribute without round_message) |
  | `video_note` | Yes | Already exists — verify it's present |
  | `gif` | Yes | Return `None` (GIFs not supported) |
  | `game` | Yes | Return `None` (games not supported) |
  | `web_preview` | Yes | Return `None` (web previews not supported) |
  | `dice` | Yes | Return `None` (dice not supported) |

  **17 new properties needed** (excluding `voice` and `video_note` which already exist).

## Implementation steps (developer-facing)

1. **Add new dataclass fields to `ServerlessMessage`** in `serverless_message.py`:
   ```python
   _sender_id: int | None = None
   _chat_id_value: int | None = None
   ```
   Use `_chat_id_value` (not `_chat_id`) to avoid name collision with the property `chat_id`. These fields are optional and default to `None`. They'll be populated by the message factory and client methods in T5.

2. **Add simple read-only properties to `serverless_message_properties.py`** (the mixin from T3):

   Properties that return `None`:
   ```python
   @property
   def forward(self) -> None:
       return None

   @property
   def via_bot(self) -> None:
       return None

   @property
   def sticker(self) -> None:
       return None

   @property
   def contact(self) -> None:
       return None

   @property
   def venue(self) -> None:
       return None

   @property
   def gif(self) -> None:
       return None

   @property
   def game(self) -> None:
       return None

   @property
   def web_preview(self) -> None:
       return None

   @property
   def dice(self) -> None:
       return None
   ```

   Properties that return field values:
   ```python
   @property
   def sender_id(self) -> int | None:
       return self._sender_id

   @property
   def chat_id(self) -> int | None:
       return self._chat_id_value

   @property
   def raw_text(self) -> str:
       return self.text

   @property
   def reply_to_msg_id(self) -> int | None:
       return None
   ```

   Properties that raise NotImplementedError:
   ```python
   @property
   def sender(self) -> object:
       raise NotImplementedError("sender requires entity resolution")

   @property
   def chat(self) -> object:
       raise NotImplementedError("chat requires entity resolution")
   ```

   Properties derived from document:
   ```python
   @property
   def audio(self) -> Document | None:
       if self._media_document is None:
           return None
       for attr in self._media_document.attributes:
           if isinstance(attr, DocumentAttributeAudio) and not attr.voice:
               return self._media_document
       return None

   @property
   def video(self) -> Document | None:
       if self._media_document is None:
           return None
       for attr in self._media_document.attributes:
           if isinstance(attr, DocumentAttributeVideo) and not attr.round_message:
               return self._media_document
       return None
   ```

3. **Verify line counts**: Both `serverless_message.py` and `serverless_message_properties.py` must stay under 200 lines. The mixin gains ~70 lines of properties (from ~90 to ~160). The main file gains ~4 lines (2 new fields + 1 import change). Both should be well under 200.

4. **Remove xfail marker** from `tests/unit/test_telethon_conformance_message_extended.py`:
   - Remove `@pytest.mark.xfail(strict=True, reason="Divergence: missing message properties")` from `test_message_additional_properties`

5. **Run `make check`** — must be 100% green.

## Production safety constraints (mandatory)

N/A — testing library, no production resources.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: `audio` and `video` properties follow the same pattern as existing `voice` and `video_note`.
- **Correct file locations**: additions to existing files, following established patterns.
- **No regressions**: existing tests pass; 1 new test transitions from xfail to pass.

## Error handling + correctness rules (mandatory)

- `sender` and `chat` properties raise `NotImplementedError` — do not return None or fake objects.
- Properties returning `None` are by design (not silencing errors) — these represent unsupported media types.

## Zero legacy tolerance rule (mandatory)

- Remove the 1 `@pytest.mark.xfail` decorator.
- No dead code.

## Acceptance criteria (testable)

1. All 19 properties from the test's `expected_properties` set exist on `ServerlessMessage` (17 new + 2 existing `voice`, `video_note`).
2. `test_message_additional_properties` passes (no xfail).
3. `sender_id` returns `None` by default, can be set via `_sender_id` field.
4. `chat_id` returns `None` by default, can be set via `_chat_id_value` field.
5. `raw_text` returns same value as `text`.
6. `sender` raises `NotImplementedError`.
7. `chat` raises `NotImplementedError`.
8. `audio` returns Document when AudioAttribute exists (non-voice).
9. `video` returns Document when VideoAttribute exists (non-round).
10. All files under 200 lines.
11. `make check` is 100% green.

## Verification / quality gates

- [ ] `make check` passes
- [ ] 1 previously-xfail test now passes
- [ ] `wc -l` on modified files < 200
- [ ] No new warnings introduced

## Edge cases

- Message with AudioAttribute where `voice=True`: `audio` should return `None` (it's a voice note, not audio). `voice` should return the Document (existing behavior).
- Message with VideoAttribute where `round_message=True`: `video` should return `None` (it's a video note). `video_note` should return the Document (existing behavior).
- Message with no document: `audio`, `video` both return `None`.
- `raw_text` on message with empty text: returns `""`.

## Notes / risks

- **Risk**: The test checks `hasattr(ServerlessMessage, prop)` — if a property raises `NotImplementedError`, `hasattr` still returns `True` (it's checking class-level attribute existence, not evaluating the property). This is correct behavior.
  - **Mitigation**: Verified — `hasattr` on a class checks if the descriptor exists, not if it raises when accessed on an instance. Our `sender` and `chat` properties exist as class descriptors, so `hasattr(ServerlessMessage, 'sender')` returns `True`.
