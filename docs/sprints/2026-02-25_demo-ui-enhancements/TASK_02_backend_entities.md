---
Task ID: `T2`
Title: `Add entities field to API model and serialize Telethon entities`
Depends on: —
Parallelizable: yes, with T1
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Backend support for message entities: add `entities` field to `MessageResponse` and serialize Telethon `TypeMessageEntity` objects into `{type, offset, length, url?, language?}` dicts. This enables the frontend to render formatted bot messages.

## Context (contract mapping)

- Requirements: GitHub Issue #9 — "Backend `api_models.py`: Add `entities` field to `MessageResponse`" and "Backend `serialize.py`: Serialize `message.entities`"
- Architecture: Pydantic models in `api_models.py`, serialization in `serialize.py`

## Preconditions

- None — this is an independent backend task

## Non-goals

- No frontend changes in this task
- No test changes in this task (covered by T3)
- Do not modify the `ServerlessMessage` dataclass (entities come from real Telethon messages)

## Touched surface (expected files / modules)

- `tg_auto_test/demo_ui/server/api_models.py` — add `entities` field to `MessageResponse`
- `tg_auto_test/demo_ui/server/serialize.py` — add entity serialization logic
- Possibly `tg_auto_test/demo_ui/server/serialize_entities.py` — NEW: if serialize.py exceeds 200 lines

## Dependencies and sequencing notes

- No dependencies — can run in parallel with T1 (different files entirely)
- T3 (tests) depends on this task
- T4 (frontend rendering) depends on this task

## Third-party / library research (mandatory for any external dependency)

- **Library**: Telethon (already in project, version from lockfile)
  - **Entity types**: `telethon.tl.types` contains `MessageEntityBold`, `MessageEntityItalic`, `MessageEntityUrl`, `MessageEntityTextUrl`, `MessageEntityCode`, `MessageEntityPre`, `MessageEntityUnderline`, `MessageEntityStrike`, `MessageEntitySpoiler`
  - **Common attributes**: all have `.offset` (int) and `.length` (int) — these are UTF-16 code unit offsets
  - **Special attributes**: `MessageEntityTextUrl` has `.url` (str), `MessageEntityPre` has `.language` (str)
  - **Message access**: `message.entities` returns `list[TypeMessageEntity] | None`; `message.caption_entities` available via `getattr(message, "caption_entities", None)` for media captions (Telethon stores this on the raw message)
  - **Verified**: `MessageEntityBold(offset=0, length=5)` → `.offset=0, .length=5` confirmed working

- **Library**: Pydantic v2 (already in project)
  - **Documentation**: https://docs.pydantic.dev/latest/concepts/models/
  - **Usage**: `entities: list[dict[str, str | int]] = []` as field default

## Implementation steps (developer-facing)

1. **Update `api_models.py`** — add `entities` field to `MessageResponse`:
   ```python
   entities: list[dict[str, str | int]] = []
   ```
   This field holds serialized entity dicts with keys: `type`, `offset`, `length`, and optionally `url`, `language`.

2. **Plan line count for `serialize.py`** (currently 173 lines):
   - Entity serialization needs approximately 40-50 lines (type mapping + serialize function)
   - 173 + 50 = 223 — exceeds 200-line limit
   - **Must extract entity serialization into a new file**: `serialize_entities.py`

3. **Create `tg_auto_test/demo_ui/server/serialize_entities.py`**:
   - Define `ENTITY_TYPE_MAP`: a dict mapping Telethon entity class → string type name:
     ```python
     from telethon.tl.types import (
         MessageEntityBold,
         MessageEntityItalic,
         MessageEntityUnderline,
         MessageEntityStrike,
         MessageEntityCode,
         MessageEntityPre,
         MessageEntityUrl,
         MessageEntityTextUrl,
         MessageEntitySpoiler,
     )

     ENTITY_TYPE_MAP: dict[type, str] = {
         MessageEntityBold: "bold",
         MessageEntityItalic: "italic",
         MessageEntityUnderline: "underline",
         MessageEntityStrike: "strikethrough",
         MessageEntityCode: "code",
         MessageEntityPre: "pre",
         MessageEntityUrl: "url",
         MessageEntityTextUrl: "text_url",
         MessageEntitySpoiler: "spoiler",
     }
     ```
   - Define `serialize_entity(entity: object) -> dict[str, str | int] | None`:
     - Look up `type(entity)` in `ENTITY_TYPE_MAP`
     - If not found, return `None` (skip unsupported entity types)
     - Build dict: `{"type": type_name, "offset": entity.offset, "length": entity.length}`
     - If type is `"text_url"`, add `"url": entity.url`
     - If type is `"pre"` and `entity.language`, add `"language": entity.language`
     - Return the dict
   - Define `serialize_entities(entities: list[object] | None) -> list[dict[str, str | int]]`:
     - If entities is `None` or empty, return `[]`
     - Map each entity through `serialize_entity`, filter out `None` results
     - Return the list

4. **Update `serialize.py`** — wire entity serialization into `serialize_message()`:
   - Import `serialize_entities` from `serialize_entities`
   - In the text message path (where `MessageResponse` is returned with `type="text"`), add:
     ```python
     entities=serialize_entities(getattr(message, "entities", None))
     ```
   - For media messages (photo, document, voice, video_note), serialize caption entities:
     ```python
     entities=serialize_entities(getattr(message, "caption_entities", None))
     ```
   - For the final `MessageResponse` construction (the one at line 134), add the entities field
   - For poll and invoice messages, entities are not applicable — leave as default `[]`

5. **Verify line counts**:
   - `api_models.py`: was 47 lines, adding 1 line → 48 lines ✅
   - `serialize_entities.py`: ~45 lines ✅
   - `serialize.py`: was 173 lines, adding 2-3 import + usage lines, no net growth since entity logic is in separate file → ~175 lines ✅

6. **Run `make check`** to verify linting and tests pass.

## Production safety constraints (mandatory)

- **Database operations**: N/A — no database
- **Resource isolation**: N/A — only API model and serialization changes
- **Migration preparation**: N/A — no persistent state changes

## Anti-disaster constraints (mandatory)

- **Reuse before build**: extends existing serialization module pattern
- **Correct libraries only**: Telethon (already in lockfile), Pydantic (already in lockfile)
- **Correct file locations**: `serialize_entities.py` alongside existing `serialize.py` in `tg_auto_test/demo_ui/server/`
- **No regressions**: existing serialization tests must still pass; the new `entities` field defaults to `[]` so existing responses are unchanged
- **Follow UX/spec**: entity type names match Telegram's Bot API entity type names exactly

## Error handling + correctness rules (mandatory)

- **Do not silence errors**: if `getattr` returns unexpected types, the type check in `ENTITY_TYPE_MAP` lookup will simply skip them (return `None`) — this is correct behavior for unsupported entity types, not error silencing
- Unknown entity types are gracefully skipped (not all Telegram entity types need rendering)
- `serialize_entities` never raises — it produces a best-effort list

## Zero legacy tolerance rule (mandatory)

After implementing this task:
- No duplicate serialization logic
- Entity serialization is cleanly separated into `serialize_entities.py`
- `serialize.py` remains focused on message-level serialization

## Acceptance criteria (testable)

1. `MessageResponse` model has `entities: list[dict[str, str | int]] = []` field
2. `serialize_entities.py` exists with `serialize_entities()` and `serialize_entity()` functions
3. `serialize_message()` populates `entities` for text messages using `message.entities`
4. `serialize_message()` populates `entities` for media messages using `message.caption_entities`
5. Entity dicts contain `type`, `offset`, `length` keys; `text_url` entities include `url`; `pre` entities include `language` (when present)
6. `serialize.py` remains under 200 lines
7. `api_models.py` remains under 200 lines
8. `serialize_entities.py` is under 200 lines
9. `make check` passes
10. Existing API responses are backward compatible (entities defaults to `[]`)

## Verification / quality gates

- [ ] Unit tests added/updated — deferred to T3
- [ ] Linters/formatters pass — `make check` green
- [ ] No new warnings introduced
- [ ] Negative-path tests — deferred to T3

## Edge cases

- Message with `entities=None` (most common for plain text) → empty list
- Message with unknown entity types (e.g., `MessageEntityMention`) → skipped, not in output
- `caption_entities` on media messages → properly serialized
- `MessageEntityPre` with empty language string → `language` key omitted from dict
- `MessageEntityTextUrl` always has `.url` → included in dict

## Notes / risks

- **Risk**: `serialize.py` line count is tight at 173
  - **Mitigation**: Entity logic is in a separate file; only 2-3 lines added to serialize.py for imports and usage
- **Risk**: Telethon entity `.offset`/`.length` are UTF-16 code units, not Python string indices
  - **Mitigation**: The backend passes them through as-is; UTF-16 handling is a frontend concern (T4)
