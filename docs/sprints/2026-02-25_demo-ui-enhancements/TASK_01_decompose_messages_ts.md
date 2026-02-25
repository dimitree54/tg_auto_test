---
Task ID: `T1`
Title: `Decompose messages.ts to fit under 200-line limit`
Depends on: —
Parallelizable: yes, with T2
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Split `web/src/ui/messages.ts` (currently 296 lines) into focused modules so every file stays under 200 lines. This unblocks all subsequent frontend tasks (T4, T5, T6) that modify message rendering.

## Context (contract mapping)

- Requirements: `AGENTS.md` — "Files must not exceed 200 lines... plan logical file decomposition refactoring"
- Architecture: existing codebase convention — `web/src/ui/` directory houses UI rendering modules
- Related: Prerequisite for T4, T5, T6

## Preconditions

- None — this is the first task

## Non-goals

- No behavior changes — pure structural refactoring
- No new features added in this task
- Do not change any CSS or HTML

## Touched surface (expected files / modules)

- `web/src/ui/messages.ts` — split into multiple files
- `web/src/ui/messages_media.ts` — NEW: photo, audio, video_note, document message rendering
- `web/src/ui/messages_invoice.ts` — NEW: invoice message rendering
- `web/src/ui/messages_core.ts` — NEW: shared helpers (createBubble, scrollBottom, metaHtml)
- `web/src/flows/send.ts` — update imports
- `web/src/flows/autostart.ts` — update imports
- `web/src/flows/reset.ts` — update imports
- `web/src/ui/keyboards_inline.ts` — check if it imports from messages

## Dependencies and sequencing notes

- No dependencies — this is a pure refactoring task
- Can run in parallel with T2 (backend entities) since they touch completely different files
- Must complete before T4, T5, T6 which modify message rendering files

## Third-party / library research (mandatory for any external dependency)

No third-party libraries involved — this is a pure TypeScript refactoring of existing modules.

## Implementation steps (developer-facing)

1. **Analyze current `messages.ts` (296 lines) and plan the split:**
   - Lines 1–13: imports
   - Lines 14–19: `BubbleType`, `scrollBottom()`
   - Lines 21–28: `createBubble()`
   - Lines 30–32: `metaHtml()`
   - Lines 34–40: `addTextMessage()`
   - Lines 42–55: `addPhotoMessage()`
   - Lines 57–141: `addAudioMessage()` (85 lines — the largest single function)
   - Lines 143–156: `addVideoNoteMessage()`
   - Lines 158–176: `addDocumentMessage()`
   - Lines 178–243: `addInvoiceMessage()` + `invoiceAmountLabel()` (66 lines)
   - Lines 245–296: `renderBotResponse()` (52 lines)

2. **Create `web/src/ui/messages_core.ts`** — shared helpers:
   - Move `BubbleType` type alias
   - Move `scrollBottom()`, `createBubble()`, `metaHtml()`
   - Export all of them

3. **Create `web/src/ui/messages_media.ts`** — media message rendering:
   - Move `addPhotoMessage()`, `addAudioMessage()`, `addVideoNoteMessage()`, `addDocumentMessage()`
   - Import `BubbleType`, `createBubble`, `metaHtml`, `scrollBottom` from `messages_core`
   - Import `escapeHtml` from `utils/escape`
   - Import `fmtTime`, `timeStr` from `utils/time`
   - Import `getEls` from `./dom`

4. **Create `web/src/ui/messages_invoice.ts`** — invoice message rendering:
   - Move `invoiceAmountLabel()` and `addInvoiceMessage()`
   - Import shared helpers from `messages_core`
   - Import `payInvoice` from `api/bot`, `appState` from `state/app`, etc.
   - Import `addTextMessage` and `renderBotResponse` from `messages` (will be in reduced messages.ts)

5. **Update `web/src/ui/messages.ts`** to keep only:
   - `addTextMessage()` (since it's the simplest and most widely imported)
   - `renderBotResponse()` (the main dispatch function)
   - Re-export everything from the sub-modules for backward-compatible imports:
     - `export { addPhotoMessage, addAudioMessage, addVideoNoteMessage, addDocumentMessage } from './messages_media'`
     - No re-export of invoice (only used by renderBotResponse internally)

6. **Handle circular dependency between `messages.ts` and `messages_invoice.ts`:**
   - `addInvoiceMessage` calls `renderBotResponse` and `addTextMessage` (from messages.ts)
   - `renderBotResponse` calls `addInvoiceMessage` (from messages_invoice.ts)
   - Solution: pass `renderBotResponse` and `addTextMessage` as callback parameters to `addInvoiceMessage`, OR import from messages_invoice.ts in messages.ts (no circle since messages.ts doesn't export to messages_invoice.ts anymore — messages_invoice.ts imports from messages_core.ts only)
   - Actually the cleanest approach: `messages_invoice.ts` receives `renderBotResponse` and `addTextMessage` as function parameters in `addInvoiceMessage()`. This avoids the circular import.
   - Alternative: keep `addInvoiceMessage` in `messages.ts` if the line count allows. Since `addInvoiceMessage` + `invoiceAmountLabel` is ~66 lines and `addTextMessage` + `renderBotResponse` is ~60 lines, plus imports and helpers that's about 140-150 lines — fits under 200.

7. **Revised plan (simpler, avoids circular deps):**
   - `messages_core.ts`: `BubbleType`, `scrollBottom`, `createBubble`, `metaHtml` (~35 lines)
   - `messages_media.ts`: `addPhotoMessage`, `addAudioMessage`, `addVideoNoteMessage`, `addDocumentMessage` (~140 lines)
   - `messages.ts` (reduced): imports, `addTextMessage`, `invoiceAmountLabel`, `addInvoiceMessage`, `renderBotResponse` (~160 lines) — keeps invoice + dispatch together to avoid circular deps

8. **Update imports in consuming files:**
   - `web/src/flows/send.ts`: imports `addPhotoMessage`, `addAudioMessage`, `addVideoNoteMessage`, `addDocumentMessage` — update to import from `./ui/messages_media` OR keep importing from `./ui/messages` if re-exported
   - `web/src/flows/autostart.ts`: imports `addTextMessage`, `renderBotResponse` — no change needed (still in messages.ts)
   - `web/src/flows/reset.ts`: imports `addTextMessage` — no change needed
   - `web/src/ui/keyboards_inline.ts`: check what it imports — likely `renderBotResponse` and `addTextMessage`
   - Decision: re-export media functions from `messages.ts` so external consumers don't need to change imports

9. **Verify line counts:**
   - `messages_core.ts`: ~35 lines ✅
   - `messages_media.ts`: ~140 lines ✅
   - `messages.ts` (reduced): ~160 lines ✅

10. **Run `make check`** to verify no regressions.

## Production safety constraints (mandatory)

- **Database operations**: N/A — no database involved
- **Resource isolation**: N/A — frontend-only change, no server resources affected
- **Migration preparation**: N/A

## Anti-disaster constraints (mandatory)

- **Reuse before build**: reusing existing functions, only moving them between files
- **Correct libraries only**: no new libraries
- **Correct file locations**: all new files in `web/src/ui/` following existing convention
- **No regressions**: `make check` must pass; all existing tests must pass; TypeScript compilation must succeed
- **Follow UX/spec**: no UX changes in this task

## Error handling + correctness rules (mandatory)

- **Do not silence errors**: no error handling changes in this task
- No new error handling code — pure structural move
- Preserve all existing error handling exactly as-is

## Zero legacy tolerance rule (mandatory)

After implementing this task:
- No duplicate function definitions across files
- No dead imports
- All consuming files import from correct locations
- `messages.ts` is under 200 lines

## Acceptance criteria (testable)

1. `messages_core.ts` exists and exports `BubbleType`, `scrollBottom`, `createBubble`, `metaHtml`
2. `messages_media.ts` exists and exports `addPhotoMessage`, `addAudioMessage`, `addVideoNoteMessage`, `addDocumentMessage`
3. `messages.ts` is under 200 lines
4. `messages_core.ts` and `messages_media.ts` are each under 200 lines
5. `make check` passes (all linters, formatters, tests green)
6. `npx tsc --noEmit` passes (TypeScript compiles without errors)
7. All existing functionality works identically — no behavior change
8. No duplicate function definitions exist across the split files

## Verification / quality gates

- [x] Unit tests added/updated (where applicable) — no new tests needed, existing tests cover behavior
- [ ] Integration/e2e tests updated (where applicable) — N/A
- [ ] Linters/formatters pass — `make check` green
- [ ] No new warnings introduced
- [ ] Negative-path tests exist for important failures — N/A (pure refactor)

## Edge cases

- Circular dependency between `messages.ts` and `messages_invoice.ts` — resolved by keeping invoice rendering in `messages.ts`
- Re-exports must cover all symbols that external modules import from `messages.ts`

## Notes / risks

- **Risk**: Missing a re-export breaks an import in another file
  - **Mitigation**: `npx tsc --noEmit` will catch immediately; also `make check` runs the full build
- **Risk**: jscpd may flag the re-export lines as duplication
  - **Mitigation**: Re-exports are single-line `export { ... } from '...'` — not code duplication
