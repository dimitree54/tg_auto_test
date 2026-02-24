# TASK_03 — Add poll CSS styles

---
Task ID: `T3`
Title: Add poll CSS styles (`.poll-question`, `.poll-options`, `.poll-option-btn`)
Depends on: —
Parallelizable: yes (with T1 and T2 — different file)
Owner: Developer
Status: `planned`
---

## Goal / value

Poll UI elements (question text, options container, option buttons) must be styled consistently with the existing inline keyboard pattern (`.inline-keyboard`, `.ik-btn`). Currently, no CSS rules exist for `.poll-question`, `.poll-options`, or `.poll-option-btn`, so poll buttons render as unstyled browser-default elements.

## Context (contract mapping)

- Requirements: N/A (bugfix — styles should have been included with poll support)
- Architecture: N/A (bugfix)
- Related sprints: `2026-02-23_poll-support` (introduced poll HTML structure but omitted CSS)

## Preconditions

- `make check` passes on the current codebase (or after T1/T2 if executed sequentially)

## Non-goals

- Reformatting or prettifying `app.css`
- Changing existing CSS rules
- Adding CSS for any elements other than `.poll-question`, `.poll-options`, `.poll-option-btn`

## Touched surface (expected files / modules)

- `tg_auto_test/demo_ui/server/static/ui/app.css` — append new rules at end of the single minified line

## Dependencies and sequencing notes

- No dependencies on T1 or T2. This task modifies `app.css`, while T1/T2 modify `app.js`.
- Executed last by convention.

## Third-party / library research (mandatory for any external dependency)

No third-party libraries. Standard CSS properties only.

**Reference pattern** — existing `.inline-keyboard` / `.ik-btn` rules in `app.css`:

```css
.inline-keyboard{display:flex;flex-direction:column;gap:4px;margin-top:6px;margin-bottom:4px}
.inline-keyboard .ik-btn{flex:1;border:1px solid var(--accent);border-radius:6px;padding:8px 12px;background:transparent;color:var(--accent);font-size:13px;font-weight:500;cursor:pointer;transition:background .15s,color .15s;text-align:center}
.inline-keyboard .ik-btn:hover{background:var(--accent);color:#fff}
.inline-keyboard .ik-btn:disabled{opacity:.5;cursor:not-allowed}
```

The poll styles must follow this pattern: same `var(--accent)` color, same `border-radius: 6px`, similar padding, same hover/disabled states.

## Implementation steps (developer-facing)

### Step 1: Append minified CSS rules to app.css

The file is a single minified line. Append the following CSS string to the **end** of the existing line (no newline before it — it must remain a single line):

```
.poll-question{font-size:14px;font-weight:600;margin-bottom:6px}.poll-options{display:flex;flex-direction:column;gap:4px}.poll-option-btn{width:100%;border:1px solid var(--accent);border-radius:6px;padding:8px 12px;background:transparent;color:var(--accent);font-size:13px;font-weight:500;cursor:pointer;transition:background .15s,color .15s;text-align:left}.poll-option-btn:hover{background:var(--accent);color:#fff}.poll-option-btn:disabled{opacity:.5;cursor:not-allowed}
```

**Rules breakdown**:

1. **`.poll-question`**: `font-size:14px;font-weight:600;margin-bottom:6px`
   - Matches the message font-size (14px). Bold weight (600) for the question heading. Bottom margin separates question from options.

2. **`.poll-options`**: `display:flex;flex-direction:column;gap:4px`
   - Flex column layout with 4px gap — identical to `.inline-keyboard` layout.

3. **`.poll-option-btn`**: `width:100%;border:1px solid var(--accent);border-radius:6px;padding:8px 12px;background:transparent;color:var(--accent);font-size:13px;font-weight:500;cursor:pointer;transition:background .15s,color .15s;text-align:left`
   - Mirrors `.ik-btn` styling: same accent border, border-radius, padding, colors, font, cursor, and transition.
   - Differences from `.ik-btn`: `width:100%` (poll options are full-width, not flex items in a row), `text-align:left` (poll option text reads naturally left-aligned, unlike centered keyboard buttons).

4. **`.poll-option-btn:hover`**: `background:var(--accent);color:#fff`
   - Identical to `.ik-btn:hover`.

5. **`.poll-option-btn:disabled`**: `opacity:.5;cursor:not-allowed`
   - Identical to `.ik-btn:disabled`.

### Step 2: Verify the file remains a single line

The file must still be exactly 1 line after the edit. No newlines should be introduced.

### Step 3: Run `make check`

```bash
make check
```

Must be 100% green.

## Production safety constraints (mandatory)

- **Database operations**: None. This is a static CSS file change.
- **Resource isolation**: The development `app.css` is in a separate directory from the production instance. No shared resources are affected.
- **Migration preparation**: N/A.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: Reuses existing CSS custom property `var(--accent)` and follows established button styling patterns.
- **Correct file locations**: Edit is to the existing `app.css` in its current location.
- **No regressions**: New rules only target new selectors (`.poll-question`, `.poll-options`, `.poll-option-btn`). No existing rules are modified.
- **Follow UX/spec**: Poll buttons will look consistent with inline keyboard buttons (same accent color, border-radius, hover/disabled states).

## Error handling + correctness rules (mandatory)

- N/A — CSS only. No error handling involved.

## Zero legacy tolerance rule (mandatory)

- No dead code. New rules added for new elements — nothing to remove.

## Acceptance criteria (testable)

1. `app.css` contains a `.poll-question` rule with `font-size:14px`, `font-weight:600`, `margin-bottom:6px`.
2. `app.css` contains a `.poll-options` rule with `display:flex`, `flex-direction:column`, `gap:4px`.
3. `app.css` contains a `.poll-option-btn` rule with `border:1px solid var(--accent)`, `border-radius:6px`, `padding:8px 12px`, accent-colored text, hover state, and disabled state.
4. `.poll-option-btn:hover` sets `background:var(--accent);color:#fff` (matches `.ik-btn:hover`).
5. `.poll-option-btn:disabled` sets `opacity:.5;cursor:not-allowed` (matches `.ik-btn:disabled`).
6. The file remains a single minified line (no newlines introduced).
7. `make check` passes 100% green.

## Verification / quality gates

- [ ] `make check` passes (linter + all tests green)
- [ ] No new warnings introduced
- [ ] Manual verification: `wc -l app.css` returns `1` (still single line)
- [ ] Manual verification: search `app.css` for `.poll-question`, `.poll-options`, `.poll-option-btn` — all present

## Edge cases

- Existing CSS already ends without a trailing semicolon or closing brace followed by nothing — the appended rules start with `.poll-question{` which is valid CSS concatenation after a `}` or any other rule terminator.

## Rollout / rollback

- Rollout: Deploy updated `app.css`
- Rollback: Revert the commit (removes poll CSS rules)

## Notes / risks

- **Risk**: Appending to a single-line minified file — accidentally introducing a newline would change the file from 1 line to 2 lines.
  - **Mitigation**: Verification step explicitly checks `wc -l` output. Use string append, not line append.
- **Risk**: CSS specificity conflicts — `.poll-option-btn` could be overridden by other rules.
  - **Mitigation**: No existing rules target `.poll-option-btn`. The selector specificity is equivalent to other button rules in the file.
