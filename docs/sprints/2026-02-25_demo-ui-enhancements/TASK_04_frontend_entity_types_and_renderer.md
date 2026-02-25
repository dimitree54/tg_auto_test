---
Task ID: `T4`
Title: `Add entity types, rendering util, and wire into message display`
Depends on: T1, T2
Parallelizable: yes, with T3, T6
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Create the frontend entity rendering pipeline: TypeScript types for message entities, a `renderEntities()` utility that converts entity-annotated text to HTML, and wire it into bot message display replacing `escapeHtml()` calls.

## Context (contract mapping)

- Requirements: GitHub Issue #9 — entity rendering in the demo UI
- Architecture: frontend in `web/src/`, TypeScript with Vite build

## Preconditions

- T1 completed: `messages.ts` decomposed (under 200 lines, clear structure for modification)
- T2 completed: backend serves `entities` field in `MessageResponse`

## Non-goals

- CSS styling for entities (T5)
- Clickable `/command` links (T5)
- User-sent message entity rendering (only bot messages get entities)

## Touched surface (expected files / modules)

- `web/src/types/api.ts` — add `MessageEntity` interface, update `MessageResponse`
- `web/src/utils/formatting.ts` — NEW: `renderEntities()` function
- `web/src/ui/messages.ts` — replace `escapeHtml()` with `renderEntities()` for bot messages
- `web/src/ui/messages_media.ts` — replace `escapeHtml()` with `renderEntities()` for captions

## Dependencies and sequencing notes

- Depends on T1 (messages.ts must be decomposed first — modifications would conflict with 296-line file)
- Depends on T2 (need to know the entity data shape from backend)
- T5 depends on this task (CSS + command links)
- Can run in parallel with T3 (backend tests) and T6 (start flow)

## Third-party / library research (mandatory for any external dependency)

- **JavaScript String encoding**: JavaScript strings use UTF-16 internally. `String.length` returns UTF-16 code units. Telegram entity offsets/lengths are also UTF-16 code units. This means for BMP characters (most text), offsets map directly to JS string indices. For characters outside BMP (emoji with surrogate pairs), the mapping is also correct because both Telegram and JS use UTF-16.
  - **Key insight**: No conversion needed — JS string indices ARE UTF-16 code unit indices, which is exactly what Telegram entities use.
  - **Reference**: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/length — "The length data property of a String value contains the length of the string in UTF-16 code units."
  - **Gotcha**: `String.prototype.slice(start, end)` operates on UTF-16 code units — this is correct for our use case.

## Implementation steps (developer-facing)

1. **Update `web/src/types/api.ts`**:
   - Add `MessageEntity` interface:
     ```typescript
     export interface MessageEntity {
       type: string;
       offset: number;
       length: number;
       url?: string;
       language?: string;
     }
     ```
   - Add `entities` field to `MessageResponse`:
     ```typescript
     entities?: MessageEntity[];
     ```

2. **Create `web/src/utils/formatting.ts`** — the entity renderer:
   
   The core algorithm:
   - Takes `text: string` and `entities: MessageEntity[]`
   - If no entities, return `escapeHtml(text)`
   - Sort entities by offset ascending, then by length descending (longer entities wrap shorter ones at same offset — this handles nesting)
   - Build HTML by iterating through the text, opening/closing tags at entity boundaries
   
   Implementation approach — **event-based rendering**:
   
   a. Create "events" array: for each entity, create an "open" event at `offset` and a "close" event at `offset + length`
   b. Sort events: by position ascending; at same position, close events before open events; among opens, longer entities first (outermost first)
   c. Walk through text position by position (or between events), escaping plain text segments and inserting HTML tags at event positions
   
   Concrete implementation:
   ```typescript
   import { escapeHtml } from './escape';
   
   interface MessageEntity {
     type: string;
     offset: number;
     length: number;
     url?: string;
     language?: string;
   }
   
   function openTag(entity: MessageEntity): string {
     switch (entity.type) {
       case 'bold': return '<strong>';
       case 'italic': return '<em>';
       case 'underline': return '<u>';
       case 'strikethrough': return '<s>';
       case 'code': return '<code>';
       case 'pre': return entity.language
         ? `<pre><code class="language-${escapeHtml(entity.language)}">`
         : '<pre>';
       case 'url': return ''; // handled in text phase
       case 'text_url': return `<a href="${escapeHtml(entity.url ?? '')}" target="_blank" rel="noopener">`;
       case 'spoiler': return '<span class="tg-spoiler">';
       default: return '';
     }
   }
   
   function closeTag(entity: MessageEntity): string {
     switch (entity.type) {
       case 'bold': return '</strong>';
       case 'italic': return '</em>';
       case 'underline': return '</u>';
       case 'strikethrough': return '</s>';
       case 'code': return '</code>';
       case 'pre': return entity.language ? '</code></pre>' : '</pre>';
       case 'url': return ''; // handled in text phase
       case 'text_url': return '</a>';
       case 'spoiler': return '</span>';
       default: return '';
     }
   }
   
   export function renderEntities(text: string, entities: MessageEntity[]): string {
     if (entities.length === 0) return escapeHtml(text);
     
     // Sort: by offset asc, then length desc (longer first = outermost)
     const sorted = [...entities].sort((a, b) => 
       a.offset !== b.offset ? a.offset - b.offset : b.length - a.length
     );
     
     // Build result
     let result = '';
     let pos = 0;
     
     // Track active entities with a stack
     const active: MessageEntity[] = [];
     // ... (algorithm continues)
   }
   ```
   
   The full algorithm must handle:
   - **Nesting**: entities can be contained within other entities (e.g., bold inside a link)
   - **URL entities**: `type: 'url'` means the text itself is the URL — wrap in `<a href="${escapeHtml(textSlice)}">`
   - **Overlapping**: technically Telegram entities shouldn't overlap, but if they do, close inner before outer
   - **XSS prevention**: all plain text segments MUST go through `escapeHtml()` before insertion
   
   **Recommended simplified approach**: Since Telegram entities don't truly overlap (they either nest or are adjacent), use a simpler offset-walk:
   
   ```typescript
   export function renderEntities(text: string, entities: MessageEntity[]): string {
     if (entities.length === 0) return escapeHtml(text);
     
     const sorted = [...entities].sort((a, b) => 
       a.offset !== b.offset ? a.offset - b.offset : b.length - a.length
     );
     
     let html = '';
     let pos = 0;
     
     for (const entity of sorted) {
       // Add escaped text before this entity
       if (entity.offset > pos) {
         html += escapeHtml(text.slice(pos, entity.offset));
       }
       
       const entityText = text.slice(entity.offset, entity.offset + entity.length);
       
       if (entity.type === 'url') {
         html += `<a href="${escapeHtml(entityText)}" target="_blank" rel="noopener">${escapeHtml(entityText)}</a>`;
       } else {
         html += openTag(entity) + escapeHtml(entityText) + closeTag(entity);
       }
       
       pos = entity.offset + entity.length;
     }
     
     // Add remaining text
     if (pos < text.length) {
       html += escapeHtml(text.slice(pos));
     }
     
     return html;
   }
   ```
   
   **Note on nesting**: The simplified approach above doesn't handle nested entities (e.g., bold text containing a link). For proper nesting support, implement a recursive or stack-based approach. The developer should evaluate complexity. If nesting support is needed (likely), use the event-based approach from the first code block.

3. **File size check for `formatting.ts`**:
   - `openTag` + `closeTag` + `renderEntities` + imports ≈ 80-120 lines depending on nesting support
   - Well under 200 lines ✅

4. **Update `web/src/ui/messages.ts`** — replace `escapeHtml()` for bot messages:
   - Import `renderEntities` from `../utils/formatting`
   - Import `MessageEntity` type from `../types/api` (if needed)
   - In `renderBotResponse()`, the text message path (around current `escapeHtml(data.text || '')`):
     ```typescript
     // Before (old):
     el.innerHTML += `<span class="text">${escapeHtml(data.text || '')}</span>${metaHtml()}`;
     // After (new):
     el.innerHTML += `<span class="text">${renderEntities(data.text || '', data.entities ?? [])}</span>${metaHtml()}`;
     ```
   - Same for `addTextMessage` when `type === 'received'` — BUT `addTextMessage` is also used for user-sent messages and error messages. Handle this by:
     - Adding an overload or parameter: `addTextMessage` already takes `type: BubbleType`. Only use `renderEntities` when type is `'received'` AND entities are provided.
     - OR: create a new function `addBotTextMessage(text, entities)` and use it from `renderBotResponse`
     - **Simplest approach**: modify `addTextMessage` to accept optional `entities` parameter:
       ```typescript
       export function addTextMessage(text: string, type: BubbleType, entities?: MessageEntity[]): void {
         const el = createBubble(type);
         const content = type === 'received' && entities?.length
           ? renderEntities(text, entities)
           : escapeHtml(text);
         el.innerHTML += `<span class="text">${content}</span>${metaHtml()}`;
         // ...
       }
       ```
     - Update `renderBotResponse` call: `addTextMessage(data.text || '', 'received', data.entities)`

5. **Update `web/src/ui/messages_media.ts`** — replace `escapeHtml()` for captions:
   - Import `renderEntities` and `MessageEntity` type
   - For `addPhotoMessage`, `addVideoNoteMessage`, `addDocumentMessage` — captions can have entities:
     - Update function signatures to accept optional `entities` parameter
     - Use `renderEntities(caption, entities ?? [])` instead of `escapeHtml(caption)` for received messages
   - **However**: currently captions in `renderBotResponse` are NOT passed — the current code for photo/voice/video_note/document messages does NOT render captions from the API (the `MessageResponse` only has `text` field used by the `renderBotResponse` for media). Look at current code:
     ```typescript
     if (data.type === 'photo') {
       addPhotoMessage(`/api/file/${data.file_id || ''}`, 'received');
       return;
     }
     ```
     Captions are not currently rendered for media messages from bot. The `text` field could contain the caption. So actually:
     - For photo: pass `data.text` as caption and `data.entities` for entity rendering
     - Update `renderBotResponse` media paths to pass caption + entities
   - This is a good improvement but should be scoped carefully. The current code doesn't render captions for received media at all. Adding caption+entities for received media is part of entity rendering.

6. **Update caption rendering in `renderBotResponse`** for media types:
   ```typescript
   if (data.type === 'photo') {
     addPhotoMessage(`/api/file/${data.file_id || ''}`, 'received', data.text || undefined, data.entities);
     return;
   }
   ```
   And in `addPhotoMessage`:
   ```typescript
   if (caption) {
     const captionHtml = entities?.length ? renderEntities(caption, entities) : escapeHtml(caption);
     el.innerHTML += `<span class="caption">${captionHtml}</span>`;
   }
   ```

7. **File size check**: 
   - `messages.ts` (after T1): ~160 lines + minor edits → stays under 200 ✅
   - `messages_media.ts` (after T1): ~140 lines + entity parameters → stays under 200 ✅
   - `types/api.ts`: 47 + ~8 lines → ~55 lines ✅
   - `utils/formatting.ts`: ~80-120 lines ✅

8. **Run `make check`** to verify everything compiles and passes.

## Production safety constraints (mandatory)

- **Database operations**: N/A — no database
- **Resource isolation**: N/A — frontend-only change
- **Migration preparation**: N/A

## Anti-disaster constraints (mandatory)

- **Reuse before build**: reuses existing `escapeHtml()` inside `renderEntities()` for plain text segments
- **Correct libraries only**: no new libraries
- **Correct file locations**: `utils/formatting.ts` follows existing convention (`utils/escape.ts`, `utils/time.ts`)
- **No regressions**: messages without entities render identically to before (escapeHtml fallback)
- **Follow UX/spec**: entity type mapping matches Telegram's Bot API specification

## Error handling + correctness rules (mandatory)

- **Do not silence errors**: if `renderEntities` receives malformed entities (wrong offsets), it should still produce output without throwing — use defensive bounds checking
- **XSS prevention is critical**: all plain text segments MUST be escaped via `escapeHtml()` before insertion into innerHTML
- Entity `url` values must be escaped in href attributes via `escapeHtml()`

## Zero legacy tolerance rule (mandatory)

After implementing this task:
- `escapeHtml()` is no longer used directly in `messages.ts` or `messages_media.ts` for bot message text/captions — replaced by `renderEntities()`
- `escapeHtml()` still used for: user-sent messages, error messages, document filenames — this is correct (these don't have entities)
- No parallel old/new rendering paths for bot messages

## Acceptance criteria (testable)

1. `MessageEntity` interface exists in `types/api.ts` with `type`, `offset`, `length`, `url?`, `language?`
2. `MessageResponse` in `types/api.ts` has `entities?: MessageEntity[]` field
3. `utils/formatting.ts` exists with `renderEntities(text, entities)` function
4. `renderEntities` with empty entities returns `escapeHtml(text)`
5. `renderEntities` produces correct HTML for bold, italic, underline, strikethrough, code, pre, url, text_url, spoiler entities
6. `renderEntities` escapes plain text segments (XSS safe)
7. Bot text messages in `renderBotResponse` use `renderEntities`
8. User-sent messages still use `escapeHtml` (no entities)
9. All files remain under 200 lines
10. `make check` passes

## Verification / quality gates

- [ ] Unit tests added/updated — manual browser testing for entity rendering; no TS unit test framework in this project
- [ ] Linters/formatters pass — `make check` green
- [ ] No new warnings introduced
- [ ] Negative-path tests — empty entities fallback verified

## Edge cases

- Empty entities array → falls back to `escapeHtml()` (same as before)
- Entity offset beyond text length → defensive: skip or clamp
- Entity with zero length → produces empty tag pair (harmless)
- Emoji in text (surrogate pairs) → JS `.slice()` uses UTF-16 code units, same as entity offsets — works correctly
- `url` entity: text itself is the URL, wrap in `<a>` tag
- `text_url` entity: display text differs from URL, use `entity.url` for href
- `pre` with language → `<pre><code class="language-{lang}">...</code></pre>`
- `pre` without language → `<pre>...</pre>`
- Nested entities (bold inside text_url) → must be handled by the rendering algorithm
- `data.entities` is `undefined` (old API response) → `?? []` fallback

## Notes / risks

- **Risk**: innerHTML usage with entity rendering introduces XSS surface
  - **Mitigation**: `escapeHtml()` applied to ALL text segments and ALL attribute values (urls, language names)
- **Risk**: Nested entity rendering is algorithmically complex
  - **Mitigation**: Telegram entities are well-structured (proper nesting, no true overlaps); a sort-by-offset approach handles most cases. Developer should test with real Telegram entity examples.
- **Risk**: Caption entity rendering for media messages adds scope
  - **Mitigation**: The change is mechanical — same `renderEntities` call pattern. If it threatens file size limits, it can be deferred.
