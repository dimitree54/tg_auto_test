---
Sprint ID: `2026-02-25_demo-ui-enhancements`
Sprint Goal: `Enhance Demo UI with Telegram-like "not joined" start flow and message entity rendering`
Status: `planning`
---

## Goal

Implement two Demo UI features: (1) replace auto-`/start` with a Telegram-like "not yet joined" state showing a Start button (GitHub Issue #8), and (2) render Telegram message formatting entities (bold, italic, links, spoilers, code blocks, etc.) in bot messages (GitHub Issue #9). Add backend and frontend tests for both features.

## Scope

### In
- Remove auto-`/start` on Demo UI launch; show "not joined" placeholder state
- Add "Start" button that sends `/start` and transitions to normal chat
- Reset returns to "not joined" state
- Backend: add `entities` field to `MessageResponse` and serialize Telethon entities
- Frontend: render entities as HTML (bold, italic, underline, strikethrough, code, pre, url, text_url, spoiler)
- Frontend: make `/command` patterns in text clickable
- Frontend: CSS for spoiler, code, pre formatting
- Decompose `messages.ts` (296 lines → under 200 per file)
- Tests for entity serialization and new API model field

### Out
- No changes to the serverless client testing infrastructure itself
- No changes to `ServerlessMessage` dataclass fields (entities are already on real Telethon messages)
- No mobile/responsive layout changes beyond what the features require
- No backend state tracking for "joined" vs "not joined" (purely frontend state)

## Inputs (contracts)

- Requirements: GitHub Issue #8 (remove auto /start), GitHub Issue #9 (render entities)
- Architecture: existing codebase conventions (FastAPI + Pydantic backend, Vite + TS frontend)
- Related constraints: `AGENTS.md` (200-line file limit, `make check` must be green)

## Change digest

- **Requirement deltas**:
  - Issue #8: Demo UI must open in "not yet joined" state instead of auto-sending `/start`
  - Issue #9: Bot messages must render Telegram-style entities (bold, italic, links, etc.)
  - Issue #9 comment: `/command` patterns in text should be clickable
- **Architecture deltas**:
  - `MessageResponse` gains `entities: list[dict] = []` field
  - `serialize.py` gains entity serialization logic (may require decomposition at 173 lines)
  - `messages.ts` MUST be decomposed first (296 lines, well over 200-line limit)
  - New frontend modules: `utils/formatting.ts`, CSS for entities
  - New frontend state: "not joined" vs "active" chat state

## Task list (dependency-aware)

- **T1:** [`TASK_01_decompose_messages_ts.md`](TASK_01_decompose_messages_ts.md) (depends: —) — Decompose `messages.ts` to fit under 200-line limit
- **T2:** [`TASK_02_backend_entities.md`](TASK_02_backend_entities.md) (depends: —) — Add entities field to API model and serialize Telethon entities
- **T3:** [`TASK_03_backend_entity_tests.md`](TASK_03_backend_entity_tests.md) (depends: T2) — Add tests for entity serialization
- **T4:** [`TASK_04_frontend_entity_types_and_renderer.md`](TASK_04_frontend_entity_types_and_renderer.md) (depends: T1, T2) — Add entity types, rendering util, and wire into message display
- **T5:** [`TASK_05_entity_css_and_command_links.md`](TASK_05_entity_css_and_command_links.md) (depends: T4) — Add entity CSS styles and clickable `/command` links
- **T6:** [`TASK_06_not_joined_state.md`](TASK_06_not_joined_state.md) (depends: T1) — Implement "not yet joined" state with Start button (Issue #8)
- **T7:** [`TASK_07_cleanup_and_verify.md`](TASK_07_cleanup_and_verify.md) (depends: T3, T5, T6) — Remove legacy autostart, final verification

## Dependency graph (DAG)

- T1 → T4
- T1 → T6
- T2 → T3
- T2 → T4
- T4 → T5
- T3 → T7
- T5 → T7
- T6 → T7

## Execution plan

### Critical path
- T1 → T4 → T5 → T7

### Parallel tracks (lanes)

- **Lane A (foundation)**: T1 (decompose messages.ts)
- **Lane B (backend entities)**: T2 → T3 (parallel with T1)
- **Lane C (frontend entities)**: T4 → T5 (after T1 + T2)
- **Lane D (start flow)**: T6 (after T1, parallel with T4/T5)
- **Lane E (finalize)**: T7 (after T3, T5, T6)

## Production safety

The current application version is **running in production on this same machine** (different directory).

- **Production database**: N/A — this project has no database. State is in-memory only.
- **Shared resource isolation**: Demo server uses configurable port (default 8000). Dev instance via Vite uses a different port (default 5173) with proxy. No file system conflicts — `FileStore` is in-memory.
- **Migration deliverable**: N/A — no data model changes (Pydantic model change is API-only, in-memory).

## Definition of Done (DoD)

All items must be true:

- ✅ All tasks completed and verified
- ✅ `make check` passes (ruff format, ruff check, pylint 200-line, vulture, jscpd, pytest)
- ✅ Zero legacy tolerance: `autostart.ts` removed or repurposed; no dead code; no parallel old/new paths
- ✅ No errors are silenced (no swallowed exceptions; no "pretend success")
- ✅ No new "temporary" toggles/workarounds without explicit requirement
- ✅ All Python files ≤ 200 lines; all TS files ≤ 200 lines (enforced by linter)
- ✅ Requirements/architecture docs unchanged
- ✅ Production instance untouched

## Risks + mitigations

- **Risk**: `messages.ts` decomposition (T1) touches many imports across the codebase
  - **Mitigation**: T1 is a pure refactor with no behavior change; run `make check` + `npx tsc --noEmit` immediately after

- **Risk**: UTF-16 entity offset handling is error-prone in JavaScript
  - **Mitigation**: T4 task specifies using `String.prototype.charCodeAt` / surrogate-pair awareness; test with emoji-containing text

- **Risk**: `serialize.py` at 173 lines may exceed 200 after adding entity serialization
  - **Mitigation**: T2 explicitly plans extraction of entity serialization into a separate module if needed

- **Risk**: Entity rendering with nested/overlapping entities is complex
  - **Mitigation**: T4 specifies a sort-and-stack algorithm; entities are sorted by offset then length (longest first for nesting)

## Rollback / recovery notes

- Revert all commits from this sprint; no database or persistent state changes to undo
- If partial rollback needed: T1 (decomposition) is safe to keep even if feature tasks are reverted

## Task validation status

- Per-task validation order: T1 → T2 → T3 → T4 → T5 → T6 → T7
- Validator: self-validation + task-checker
- Outcome: pending
- Notes: Tasks created sequentially with validation after each

## Sources used

- Requirements: GitHub Issue #8, GitHub Issue #9 (as described in sprint request)
- Architecture: existing codebase (no formal architecture docs)
- Code read (for scoping only):
  - `web/src/ui/messages.ts` (296 lines — must decompose)
  - `web/src/app/init.ts`, `web/src/flows/autostart.ts`, `web/src/flows/reset.ts`
  - `web/src/flows/send.ts`, `web/src/types/api.ts`, `web/src/utils/escape.ts`
  - `web/src/ui/dom.ts`, `web/src/state/app.ts`
  - `web/src/features/commands/panel.ts`
  - `web/index.html`
  - `tg_auto_test/demo_ui/server/serialize.py` (173 lines)
  - `tg_auto_test/demo_ui/server/api_models.py`
  - `tg_auto_test/demo_ui/server/routes.py`
  - `tg_auto_test/demo_ui/server/demo_server.py`
  - `tests/unit/test_demo_serialize.py` (150 lines)
  - `tests/unit/test_demo_server.py`, `tests/unit/test_demo_integration.py`
  - `tests/unit/demo_server_mocks.py`
  - `tg_auto_test/test_utils/serverless_message.py`, `serverless_message_properties.py`
  - `tg_auto_test/test_utils/serverless_telegram_client_core.py`
  - `web/src/styles/` (all CSS files)
  - `Makefile`

## Contract summary

### What (requirements)
- Demo UI opens in "not joined" state with placeholder text and Start button
- Pressing Start sends `/start` and shows normal chat
- Reset returns to "not joined" state
- Bot messages render Telegram entities (bold, italic, underline, strikethrough, code, pre, url, text_url, spoiler)
- `/command` patterns in text are clickable links

### How (architecture)
- Backend: `MessageResponse.entities` field + `serialize.py` entity serialization
- Frontend: `renderEntities()` util replaces `escapeHtml()` for bot messages
- Frontend: "not joined" state managed via CSS classes and DOM manipulation in `init.ts`/`reset.ts`
- `messages.ts` decomposed into focused modules before feature work

## Impact inventory (implementation-facing)

- **Flows**: autostart flow replaced by start-button flow; reset flow updated
- **Modules / interfaces**: `messages.ts` split; new `utils/formatting.ts`; `api_models.py` + `serialize.py` updated; `types/api.ts` updated
- **Data model / migrations**: N/A (in-memory API model only)
- **Security / privacy**: Entity rendering uses innerHTML — must escape plain text segments to prevent XSS
- **Performance / quality**: Entity rendering adds DOM complexity for bot messages; negligible impact

## Decisions (made from docs; not invented)

- D1: "Not joined" state is purely frontend; no backend API changes needed (Source: Issue #8 — Telegram UX is client-side)
- D2: Entity serialization maps Telethon `TypeMessageEntity` subclasses to `{type, offset, length, url?, language?}` dicts (Source: Issue #9 requirements)
- D3: `messages.ts` must be decomposed BEFORE feature work because it's at 296 lines (Source: `AGENTS.md` 200-line limit)
- D4: Entity type-to-HTML mapping follows Telegram's official entity types (Source: Issue #9 entity list)

## Non-goals

- NG1: No changes to serverless client infrastructure (Source: sprint scope — demo UI only)
- NG2: No user-sent message entity rendering (Source: Issue #9 — "Only received (bot) messages carry entities")
- NG3: No database or persistent state (Source: existing architecture — all state is in-memory)
