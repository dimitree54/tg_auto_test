---
Task ID: `T1`
Title: `Document Telethon interface contract in README and CONTRIBUTING`
Depends on: `--`
Parallelizable: `yes, with T2`
Owner: `Developer`
Status: `planned`
---

## Goal / value

README.md and CONTRIBUTING.md clearly document the "Telethon interface contract" so that all future contributors understand the rules: our fake classes must match real Telethon public interfaces exactly, extra `_`-prefixed methods are allowed, and unimplemented features must raise `NotImplementedError`.

## Context (contract mapping)

- Requirements: User-provided sprint request, principles 1-5
- Architecture: Current `README.md` and `CONTRIBUTING.md`

## Preconditions

- None (this task is independent)

## Non-goals

- Changing any code (this task is docs-only within README.md and CONTRIBUTING.md)
- Writing new standalone docs files

## Touched surface (expected files / modules)

- `README.md`
- `CONTRIBUTING.md`

## Dependencies and sequencing notes

- Fully independent; can run in parallel with any other task
- No file contention with other tasks (T2-T6 don't modify README or CONTRIBUTING)

## Third-party / library research (mandatory for any external dependency)

No third-party libraries involved in this task.

## Implementation steps (developer-facing)

1. **Edit `README.md`** -- add a new section "Telethon Interface Contract" after "Core idea" (or as a subsection of "Public API"). Content:
   - Our fake classes (`ServerlessTelegramClient`, `ServerlessMessage`, `ServerlessTelegramConversation`) MUST match real Telethon 1.42 public interfaces exactly: parameter names, positional/keyword-only markers, defaults, types, return types.
   - Extra `_`-prefixed methods (like `_pop_response`, `_api_calls`, `_process_text_message`) ARE allowed for internal test infrastructure.
   - Any Telethon public method/property we add but don't fully implement MUST raise `NotImplementedError("description")`.
   - The Demo UI works with both `ServerlessTelegramClient` and real `TelegramClient` through standard Telethon interfaces.

2. **Edit `README.md` Public API section** -- update the `ServerlessMessage` property list to remove `reply_markup_data` (it will be privatized in T4). Update method signatures to reflect the aligned interfaces (e.g., `conversation(entity, *, timeout=60.0)` instead of the old signature).

3. **Edit `CONTRIBUTING.md`** -- strengthen the "Telethon compatibility" subsection under "Common gotchas". Replace the current vague wording with:
   - "Test interfaces MUST match Telethon's public signatures exactly (not 'where possible')."
   - "Use `inspect` module conformance tests to verify interface alignment."
   - "Unimplemented Telethon features raise `NotImplementedError`, never silent no-ops."
   - "Extra `_`-prefixed methods are allowed for test infrastructure."

4. **Run `make check`** to verify no regressions.

## Production safety constraints (mandatory)

N/A -- documentation-only changes; no code, no database, no shared resources.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: Editing existing files, not creating new ones.
- **Correct file locations**: Editing repo-root `README.md` and `CONTRIBUTING.md` (standard locations).
- **No regressions**: Documentation changes only; `make check` must still pass.

## Error handling + correctness rules (mandatory)

N/A -- documentation-only task.

## Zero legacy tolerance rule (mandatory)

- Remove any outdated documentation that contradicts the new Telethon interface contract (e.g., old API signature examples in README that no longer match).

## Acceptance criteria (testable)

1. README.md contains a "Telethon Interface Contract" section (or equivalent heading) explaining the four rules.
2. README.md Public API section reflects the aligned method signatures (post-T3/T4/T5 names, not the old ones). Note: since T1 can run before T3-T5, document the *target* signatures.
3. CONTRIBUTING.md explicitly states that interfaces MUST match Telethon exactly (not "where possible").
4. `make check` passes.

## Verification / quality gates

- [ ] `make check` passes (ruff, pylint 200-line check, vulture, jscpd, pytest)
- [ ] Manual review: README contains Telethon interface contract section
- [ ] Manual review: CONTRIBUTING mentions exact Telethon matching requirement

## Edge cases

- README is 275 lines; additions must not push it past reasonable length. If needed, keep additions concise.
- CONTRIBUTING is 140 lines; well within limits.

## Notes / risks

- Since T1 runs before T3-T5, the README API signatures will temporarily describe the *target* state rather than the *current* state. This is acceptable because the sprint will bring the code into alignment with the docs.
