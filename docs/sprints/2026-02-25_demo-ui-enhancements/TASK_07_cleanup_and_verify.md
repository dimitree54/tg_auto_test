---
Task ID: `T7`
Title: `Remove legacy autostart, final verification`
Depends on: T3, T5, T6
Parallelizable: no
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Final verification that all legacy code is removed, no dead imports exist, all files are under 200 lines, and `make check` is 100% green. This is the quality gate task that ensures zero legacy tolerance and sprint DoD.

## Context (contract mapping)

- Requirements: Sprint DoD — "Zero legacy tolerance", "make check passes"
- Architecture: `AGENTS.md` — 200-line limit, `make check` must be green

## Preconditions

- T3 completed: backend entity tests pass
- T5 completed: entity CSS and command links work
- T6 completed: "not joined" state implemented, `autostart.ts` deleted

## Non-goals

- No new features
- No new tests beyond what's needed to fix any issues found

## Touched surface (expected files / modules)

- All files modified in T1-T6 — verification sweep
- `vulture_whitelist.py` — may need updates if vulture reports new unused code
- Any file with stale imports — fix them

## Dependencies and sequencing notes

- Depends on ALL previous tasks (T3, T5, T6 — which transitively include T1, T2, T4)
- Cannot run in parallel — this is the final verification task
- After this task, the sprint is done

## Third-party / library research (mandatory for any external dependency)

No new third-party dependencies. Verification uses existing tools:
- `make check` — runs ruff format, ruff check, pylint (200-line), vulture, jscpd, pytest
- `npx tsc --noEmit` — TypeScript compilation check (if available in project)

## Implementation steps (developer-facing)

1. **Verify `autostart.ts` is deleted**:
   - Confirm `web/src/flows/autostart.ts` does NOT exist
   - Grep the entire codebase for any imports of `autostart`:
     ```bash
     grep -r "autostart" web/src/
     grep -r "autoStart" web/src/
     ```
   - Fix any remaining references

2. **Verify no dead imports across all modified files**:
   - Check `web/src/app/init.ts` — no import from `flows/autostart`
   - Check `web/src/flows/reset.ts` — no import from `./autostart`
   - Check `web/src/flows/send.ts` — imports still valid after messages.ts split
   - Check `web/src/ui/messages.ts` — imports from new sub-modules correct
   - Check `web/src/ui/messages_media.ts` — imports correct
   - Check `web/src/ui/messages_core.ts` — imports correct

3. **Verify all file line counts are under 200**:
   - `web/src/ui/messages.ts` — must be under 200 (was 296, now decomposed)
   - `web/src/ui/messages_media.ts` — must be under 200
   - `web/src/ui/messages_core.ts` — must be under 200
   - `web/src/utils/formatting.ts` — must be under 200
   - `web/src/flows/start.ts` — must be under 200
   - `web/src/ui/dom.ts` — must be under 200
   - `web/src/app/init.ts` — must be under 200
   - `web/src/types/api.ts` — must be under 200
   - `tg_auto_test/demo_ui/server/api_models.py` — must be under 200
   - `tg_auto_test/demo_ui/server/serialize.py` — must be under 200
   - `tg_auto_test/demo_ui/server/serialize_entities.py` — must be under 200
   - `tests/unit/test_demo_serialize.py` — must be under 200
   - `tests/unit/test_demo_serialize_entities.py` — must be under 200

4. **Run `make check`** and fix any issues:
   - `uv run ruff format` — auto-format Python
   - `uv run ruff check --fix` — lint Python
   - `uvx pylint tg_auto_test tests --disable=all --enable=C0302 --max-module-lines=200` — 200-line check
   - `uv run vulture tg_auto_test tests vulture_whitelist.py` — dead code detection
   - `npx jscpd --exitCode 1` — copy-paste detection
   - `uv run pytest -n auto` — all tests pass

5. **Address vulture findings**:
   - If vulture reports the new `serialize_entities` function or `serialize_entity` as unused (because it's only called from `serialize.py`), add to `vulture_whitelist.py` if needed
   - If vulture reports functions from deleted `autostart.ts` — they should already be gone
   - If new DOM functions (`showNotJoinedState`, `resetElsCache`) are flagged — they're called from JS, not Python, so N/A

6. **Address jscpd findings**:
   - Check that the messages.ts decomposition didn't introduce copy-paste duplication
   - If re-exports in `messages.ts` trigger jscpd, verify they are minimal single-line exports (not real duplication)

7. **Verify TypeScript compiles**:
   - If `npx tsc --noEmit` is available, run it
   - Otherwise, verify `npx vite build` succeeds

8. **Final manual smoke test** (if possible):
   - Start the demo server
   - Verify: opens in "not joined" state with placeholder
   - Click Start → /start sent, response rendered
   - Send a message with entities (if bot supports it) → entities rendered with formatting
   - Click Reset → returns to "not joined" state
   - Test spoiler click-to-reveal
   - Test /command link clicking

9. **Verify all acceptance criteria from previous tasks** are met.

## Production safety constraints (mandatory)

- **Database operations**: N/A
- **Resource isolation**: N/A — verification only
- **Migration preparation**: N/A

## Anti-disaster constraints (mandatory)

- **Reuse before build**: no new code — verification and cleanup only
- **Correct libraries only**: N/A
- **Correct file locations**: only fix misplaced files if found
- **No regressions**: `make check` is the definitive regression gate
- **Follow UX/spec**: visual verification against requirements

## Error handling + correctness rules (mandatory)

- **Do not silence errors**: if `make check` reports issues, fix them properly (don't add lint ignores or silence)
- Address every warning and error
- Do not add `# noqa` or similar suppressions for new code

## Zero legacy tolerance rule (mandatory)

This task IS the zero-legacy enforcement:
- `autostart.ts` deleted
- No dead imports
- No unused functions
- No parallel old/new paths
- No "TODO" or "FIXME" left behind from this sprint's work

## Acceptance criteria (testable)

1. `make check` is 100% green (all linters, tests pass)
2. `web/src/flows/autostart.ts` does not exist
3. No import of `autostart` or `autoStart` exists anywhere in the codebase
4. All Python files are under 200 lines (pylint check passes)
5. All TypeScript files are under 200 lines
6. No new `# noqa` or lint suppression comments added for sprint code
7. `vulture` reports no new dead code from this sprint
8. `jscpd` reports no new copy-paste duplication from this sprint
9. All pytest tests pass

## Verification / quality gates

- [ ] `make check` passes (this IS the verification)
- [ ] No new warnings introduced
- [ ] All files from T1-T6 verified under 200 lines
- [ ] Codebase grep confirms no stale references to deleted files

## Edge cases

- Vulture may flag `serialize_entities` module — add to whitelist only if genuinely a false positive (it's imported and used in `serialize.py`)
- jscpd may flag re-export patterns — verify they're minimal and not real duplication

## Notes / risks

- **Risk**: `make check` finds issues that require changes in multiple task areas
  - **Mitigation**: This task is scheduled last specifically to catch cross-task issues; fixes are scoped to what's needed
- **Risk**: Vulture false positives on new code
  - **Mitigation**: Only add to whitelist if genuinely false positive; otherwise fix the dead code
