---
Task ID: `T6`
Title: `Add ~8 conversation stubs and ~4 button stubs`
Depends on: T1
Parallelizable: yes, with T2–T5
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Add `NotImplementedError`-raising stubs for all missing Telethon `Conversation` (~8) and `MessageButton` (~4) methods/properties. After this task, the reverse conformance tests for conversation and button classes pass (all xfail markers removed).

## Context (contract mapping)

- Requirements: User's GAP 2 — ~8 missing conversation members, ~4 missing button members
- Architecture: `serverless_telegram_conversation.py` (90 lines) and `serverless_button.py` (16 lines) have ample headroom — no file decomposition needed

## Preconditions

- T1 complete (reverse conformance tests identify exact missing members)
- `make check` is green

## Non-goals

- Implementing real behavior for any stub
- File decomposition (both files have ample headroom)

## Touched surface (expected files / modules)

- `tg_auto_test/test_utils/serverless_telegram_conversation.py` (MODIFY — add ~8 stubs, from 90 to ~130 lines)
- `tg_auto_test/test_utils/serverless_button.py` (MODIFY — add ~4 stubs, from 16 to ~40 lines)
- `tests/unit/test_telethon_reverse_conformance_conversation.py` (MODIFY — remove xfail markers)
- `tests/unit/test_telethon_reverse_conformance_button.py` (MODIFY — remove xfail markers)

## Dependencies and sequencing notes

- Depends on T1 only (needs the exact list of missing members).
- Fully parallel with T2–T5 since conversation and button files are untouched by those tasks.

## Third-party / library research

- **Library**: Telethon 1.42.x
- **Conversation reference**: https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.conversation.Conversation
- **MessageButton reference**: https://docs.telethon.dev/en/stable/modules/custom.html#telethon.tl.custom.messagebutton.MessageButton
- **Conversation missing** (from audit, confirmed by T1):
  - Properties: `chat`, `chat_id`, `input_chat`, `is_channel`, `is_group`, `is_private`
  - Methods: `get_chat`, `get_input_chat`
  - These come from `ChatGetter` mixin that Telethon's `Conversation` inherits from.
- **Button missing** (from audit, confirmed by T1):
  - Properties: `client`, `inline_query`, `url`
  - Methods: `click`
  - Note: Our `ServerlessButton` is a frozen dataclass. Properties can be added as `@property` on the class. The `click` method on `MessageButton` is different from `Message.click` — it's the button-level click.

## Implementation steps (developer-facing)

1. **Run T1's conversation and button reverse conformance tests** to get exact lists:
   ```
   uv run pytest tests/unit/test_telethon_reverse_conformance_conversation.py -v 2>&1 | grep XFAIL
   uv run pytest tests/unit/test_telethon_reverse_conformance_button.py -v 2>&1 | grep XFAIL
   ```

2. **Add conversation stubs to `serverless_telegram_conversation.py`**:
   - `ChatGetter` properties — these are properties from Telethon's `ChatGetter` that `Conversation` inherits:
     ```python
     @property
     def chat(self) -> object:
         raise NotImplementedError("chat requires entity resolution")

     @property
     def chat_id(self) -> int | None:
         raise NotImplementedError("chat_id is not tracked in serverless mode")

     @property
     def input_chat(self) -> object:
         raise NotImplementedError("input_chat requires entity resolution")

     @property
     def is_channel(self) -> bool:
         raise NotImplementedError("is_channel requires entity resolution")

     @property
     def is_group(self) -> bool:
         raise NotImplementedError("is_group requires entity resolution")

     @property
     def is_private(self) -> bool:
         raise NotImplementedError("is_private requires entity resolution")

     async def get_chat(self) -> object:
         raise NotImplementedError("get_chat requires entity resolution")

     async def get_input_chat(self) -> object:
         raise NotImplementedError("get_input_chat requires entity resolution")
     ```
   - Check Telethon source to confirm sync/async for each.

3. **Add button stubs to `serverless_button.py`**:
   - `client` property: `@property def client(self): raise NotImplementedError("client reference is not available in serverless mode")`
   - `inline_query` property: `@property def inline_query(self): raise NotImplementedError("inline_query is not supported")`
   - `url` property: `@property def url(self): raise NotImplementedError("url is not supported")`
   - `click` method: `async def click(self, *args, **kwargs): raise NotImplementedError("button-level click() is not supported in serverless mode")`
   - Note: `ServerlessButton` is `@dataclass(frozen=True, slots=True)`. Properties defined on the class work fine with slots+frozen. The `click` method also works — methods are class-level, not instance attributes.

4. **Update reverse conformance tests**:
   - Remove xfail markers for conversation and button members in:
     - `tests/unit/test_telethon_reverse_conformance_conversation.py`
     - `tests/unit/test_telethon_reverse_conformance_button.py`

5. **Run `make check`** — must be 100% green.

6. **Verify line counts**: Conversation file should be ~130 lines, button file ~40 lines.

## Production safety constraints (mandatory)

N/A — testing library, no production resources.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: Adding stubs to existing files that have headroom.
- **Correct file locations**: Modifying existing files in-place.
- **No regressions**: Existing tests pass; xfail markers removed only for added stubs.

## Error handling + correctness rules (mandatory)

- Every stub raises `NotImplementedError` with a descriptive message.
- No silent fallbacks or empty returns.

## Zero legacy tolerance rule (mandatory)

- All xfail markers for conversation and button members removed.
- No dead code.

## Acceptance criteria (testable)

1. All ~8 missing conversation methods/properties exist on `ServerlessTelegramConversation`.
2. All ~4 missing button methods/properties exist on `ServerlessButton`.
3. Each stub raises `NotImplementedError` when called/accessed.
4. Reverse conformance tests for conversation and button pass with no xfail markers.
5. Both files under 200 lines.
6. `make check` is 100% green.

## Verification / quality gates

- [ ] `make check` passes
- [ ] `uv run pytest tests/unit/test_telethon_reverse_conformance_conversation.py -v` — all pass
- [ ] `uv run pytest tests/unit/test_telethon_reverse_conformance_button.py -v` — all pass
- [ ] `wc -l` on both files shows < 200
- [ ] No new warnings introduced

## Edge cases

- `ServerlessButton` is `@dataclass(frozen=True, slots=True)` — confirm that `@property` and regular methods work on frozen+slots dataclasses. They do: properties and methods are class-level descriptors, not instance attributes.
- Conversation's `chat` property conflicts with the name — `ServerlessTelegramConversation` doesn't currently have a `chat` attribute, so no conflict.
- `chat_id` may conflict if `Conversation` also has it as an attribute — check Telethon source. In Telethon, `chat_id` is a property from `ChatGetter`.

## Notes / risks

- **Risk**: Minimal risk — both files have ample headroom and the stubs are simple.
  - **Mitigation**: N/A — straightforward task.
