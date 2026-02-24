# Sprint: Demo UI Poll & Photo Rendering Fixes

---
Sprint ID: `2026-02-24_demo-ui-poll-fixes`
Sprint Goal: Fix three Demo UI rendering bugs — poll onclick handlers destroyed by `innerHTML +=`, photo load handler orphaned by `innerHTML +=`, and missing poll CSS styles.
Status: `planning`
---

## Goal

Fix three bugs in the Demo UI front-end (`app.js` and `app.css`) that cause poll buttons to lose click handlers, photo load events to fire on detached DOM nodes, and poll elements to render without styling. All fixes are strictly scoped to the minified front-end assets.

## Scope

### In
- Fix `innerHTML +=` in `Pe()` (poll render) to use `insertAdjacentHTML` and consolidate dead `Me()` function into `P()`
- Fix `innerHTML +=` in `se()` (photo render) to use `insertAdjacentHTML` so `<img>` load handler fires on live DOM node
- Add missing `.poll-question`, `.poll-options`, `.poll-option-btn` CSS rules to `app.css`

### Out
- Any changes to Python server code, test files, or other front-end files
- Reformatting or prettifying the minified JS/CSS
- Functional changes beyond the three identified bugs

## Inputs (contracts)

- Requirements: N/A — pure bugfix sprint, no requirement changes
- Architecture: N/A — no architectural changes
- Related constraints/ADRs: N/A

## Change digest

No requirement or architecture deltas. This sprint addresses three rendering bugs discovered in the Demo UI front-end that shipped with the poll support feature (sprint `2026-02-23_poll-support`).

- **Requirement deltas**: None
- **Architecture deltas**: None
- **Bug origins**:
  - `Me()` function passes a `Date` object to `I()` which expects seconds — produces garbled timestamps like "30437542:24"
  - `innerHTML +=` in `Pe()` serializes+re-parses DOM, destroying `.onclick` handlers on poll option buttons
  - `innerHTML +=` in `se()` orphans the `<img>` element so its `load` event listener references a detached node
  - No CSS rules exist for `.poll-question`, `.poll-options`, `.poll-option-btn`

## Task list (dependency-aware)

- **T1:** [TASK_01.md](TASK_01.md) (depends: —) — Fix poll event handlers destroyed by `innerHTML +=` and remove dead `Me()` function
- **T2:** [TASK_02.md](TASK_02.md) (depends: —) — Fix photo load handler destroyed by `innerHTML +=`
- **T3:** [TASK_03.md](TASK_03.md) (depends: —) — Add poll CSS styles

## Dependency graph (DAG)

All three tasks are independent — they touch different functions (T1: `Pe()`/`Me()`, T2: `se()`) or different files (T3: `app.css`).

```
T1 (no deps)
T2 (no deps)
T3 (no deps)
```

No edges. All tasks could theoretically run in parallel, but per sprint process they execute sequentially: T1 → T2 → T3.

## Execution plan

### Critical path
T1 → T2 → T3 (sequential by process convention, not by dependency)

### Parallel tracks (lanes)
All tasks are independent. Sequential execution is a process constraint, not a technical one.

- **Lane A**: T1, T2, T3 (single lane, sequential)

## Production safety

The current application version is **running in production on this same machine** (different directory).

- **Production database**: N/A — these changes are purely front-end (static JS/CSS). No database operations.
- **Shared resource isolation**: Changes are to static asset files only (`app.js`, `app.css`). The development copy is in a separate directory from production. No ports, sockets, or shared resources are affected.
- **Migration deliverable**: N/A — no data model changes.

## Definition of Done (DoD)

All items must be true:

- ✅ All three tasks completed and verified
- ✅ `make check` passes 100% green after each task
- ✅ Zero legacy tolerance: dead `Me()` function removed; no duplicate code paths
- ✅ No errors are silenced
- ✅ No new "temporary" toggles/workarounds
- ✅ Requirements/architecture docs unchanged
- ✅ Production database untouched (N/A — front-end only)
- ✅ No shared local resources conflict with production instance
- ✅ No debug artifacts, no TODO/FIXME comments in changed code

## Risks + mitigations

- **Risk**: `app.js` is minified — edits must preserve exact formatting (no reformatting, no line breaks).
  - **Mitigation**: Each task specifies exact before/after strings for surgical replacement. Developer must use precise string matching, not regex-based reformatting.
- **Risk**: `app.css` is single-line minified — new CSS must be appended in the same minified style.
  - **Mitigation**: Task 3 provides the exact minified CSS string to append.
- **Risk**: `jscpd` (copy-paste detector) might flag the `insertAdjacentHTML` pattern used in both T1 and T2.
  - **Mitigation**: Low risk — surrounding code context differs significantly. Monitor `make check` output.
- **Risk**: Surgical edits to minified code could introduce syntax errors.
  - **Mitigation**: `make check` after each task catches any breakage immediately.

## Migration plan (if data model changes)

N/A — no data model changes.

## Rollback / recovery notes

- Revert the commits for T1/T2/T3. All changes are isolated to `app.js` and `app.css`. No data migrations or config changes to undo.

## Task validation status

- T1: `TASK_01.md` — pending
- T2: `TASK_02.md` — pending
- T3: `TASK_03.md` — pending

## Sources used

- Requirements: N/A (bugfix sprint)
- Architecture: N/A (bugfix sprint)
- Code read (for scoping only):
  - `tg_auto_test/demo_ui/server/static/ui/app.js` (lines 285-293, 350-414)
  - `tg_auto_test/demo_ui/server/static/ui/app.css` (full file — 1 minified line)

## Contract summary

### What (requirements)
- Poll option buttons must retain onclick handlers after rendering
- Photo load handler must fire on the live DOM node
- Poll UI elements must be styled consistently with existing inline keyboard pattern

### How (architecture)
- Replace `innerHTML +=` with `insertAdjacentHTML("beforeend", ...)` in `Pe()` and `se()`
- Remove dead `Me()` function, use `P()` throughout
- Append minified CSS rules for `.poll-question`, `.poll-options`, `.poll-option-btn`

## Impact inventory (implementation-facing)

- **Flows**: Poll message rendering (`Pe()`), photo message rendering (`se()`)
- **Modules / interfaces**: `app.js` (functions `Pe`, `se`, `Me`), `app.css` (new selectors)
- **Data model / migrations**: None
- **Security / privacy**: None
- **Performance / quality**: Fixes event handler leaks; no performance regressions

## Decisions (made from docs; not invented)

- D1: Use `P()` instead of `Me()` — `Me()` is a buggy duplicate of `P()` (Source: code analysis of `app.js` lines 285-293, 353-355, 399-401)
- D2: Use `insertAdjacentHTML("beforeend", ...)` instead of `innerHTML +=` — standard DOM API that appends HTML without re-parsing existing nodes (Source: bug report)
- D3: Poll CSS follows `.inline-keyboard` / `.ik-btn` pattern — accent color, border-radius, padding, hover/disabled states (Source: bug report + existing CSS)

## Non-goals

- NG1: Reformatting or prettifying minified JS/CSS (Source: sprint decision — preserve minified format)
- NG2: Fixing any bugs outside the three identified issues (Source: sprint scope)
- NG3: Modifying Python server code or test files (Source: sprint scope)
