# TASK_02 — Fix photo load handler destroyed by innerHTML +=

---
Task ID: `T2`
Title: Fix photo load handler destroyed by `innerHTML +=` in `se()`
Depends on: —
Parallelizable: yes (with T1 and T3 — different function/file)
Owner: Developer
Status: `planned`
---

## Goal / value

The `<img>` element's `load` event handler in `se()` must fire on the live DOM node so the chat auto-scrolls after the image loads. Currently, `innerHTML +=` on lines 408 re-parses the container, replacing the original `<img>` element with a new one that has no event listener.

## Context (contract mapping)

- Requirements: N/A (bugfix)
- Architecture: N/A (bugfix)
- Related sprints: Photo rendering existed before `2026-02-23_poll-support`; the bug pre-dates that sprint.

## Preconditions

- `make check` passes on the current codebase (or after T1 if executed sequentially)

## Non-goals

- Reformatting or prettifying `app.js`
- Changing any function other than `se()`
- Fixing the separate `b()` function (line 402-404) which also uses `innerHTML +=` but does not have the event listener problem since it appends text+timestamp in a single assignment before DOM insertion

## Touched surface (expected files / modules)

- `tg_auto_test/demo_ui/server/static/ui/app.js` — function `se()` (lines 406-409)

## Dependencies and sequencing notes

- No dependencies on T1 or T3. `se()` is a separate function from `Pe()` (T1) and in a different file from `app.css` (T3).
- If T1 was executed first, line numbers in `app.js` will have shifted by -3 (due to `Me()` deletion). The developer should locate `se()` by searching for `function se(` rather than relying on line numbers.

## Third-party / library research (mandatory for any external dependency)

No third-party libraries involved. The fix uses standard DOM API:

- **API**: `Element.insertAdjacentHTML(position, text)`
  - **MDN documentation**: https://developer.mozilla.org/en-US/docs/Web/API/Element/insertAdjacentHTML
  - Position `"beforeend"` inserts HTML just inside the element, after its last child — equivalent to `innerHTML +=` but without re-parsing existing children.
  - Browser support: all modern browsers (Chrome 1+, Firefox 8+, Safari 4+).
  - **Key advantage over `innerHTML +=`**: existing DOM nodes (including the `<img>` with its `load` event listener) are preserved.

## Implementation steps (developer-facing)

### Step 1: Locate `se()` in app.js

Search for `function se(` in `app.js`. The current code (line 406-409, before T1 line shifts) is:

```javascript
function se(e, t, n) {
  const s = l(), i = x(t), o = document.createElement("img");
  o.className = "msg-photo", o.src = e, o.alt = "Photo", i.appendChild(o), n && (i.innerHTML += `<span class="caption">${S(n)}</span>`), i.innerHTML += P(), s.messagesEl.appendChild(i), o.addEventListener("load", () => $()), $();
}
```

### Step 2: Replace both `innerHTML +=` calls with `insertAdjacentHTML`

Replace the entire function body line (the long single line starting with `o.className`) so that:

**Before** (the long line inside `se()`):
```
  o.className = "msg-photo", o.src = e, o.alt = "Photo", i.appendChild(o), n && (i.innerHTML += `<span class="caption">${S(n)}</span>`), i.innerHTML += P(), s.messagesEl.appendChild(i), o.addEventListener("load", () => $()), $();
```

**After**:
```
  o.className = "msg-photo", o.src = e, o.alt = "Photo", i.appendChild(o), n && i.insertAdjacentHTML("beforeend", `<span class="caption">${S(n)}</span>`), i.insertAdjacentHTML("beforeend", P()), s.messagesEl.appendChild(i), o.addEventListener("load", () => $()), $();
```

**Two changes on this line**:

1. `n && (i.innerHTML += \`<span class="caption">${S(n)}</span>\`)` → `n && i.insertAdjacentHTML("beforeend", \`<span class="caption">${S(n)}</span>\`)`
   - Removes the parentheses wrapping (not needed since `insertAdjacentHTML` is a direct method call that works as the right operand of `&&`)
2. `i.innerHTML += P()` → `i.insertAdjacentHTML("beforeend", P())`

### Step 3: Run `make check`

```bash
make check
```

Must be 100% green.

## Production safety constraints (mandatory)

- **Database operations**: None. This is a static JavaScript file change.
- **Resource isolation**: The development `app.js` is in a separate directory from the production instance. No shared resources are affected.
- **Migration preparation**: N/A.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: Uses the same `insertAdjacentHTML` DOM API pattern — no new utilities needed.
- **Correct file locations**: Edit is to the existing `app.js` in its current location.
- **No regressions**: `insertAdjacentHTML("beforeend", ...)` is semantically equivalent to `innerHTML +=` for appending, but preserves existing DOM nodes and their event listeners.
- **Follow UX/spec**: Photo messages will now auto-scroll correctly after the image loads.

## Error handling + correctness rules (mandatory)

- No error handling changes in this task.
- The fix eliminates a silent failure (load event listener on detached `<img>` node never fires, preventing auto-scroll).

## Zero legacy tolerance rule (mandatory)

- No dead code introduced or left behind. The fix is a direct replacement of two expressions.

## Acceptance criteria (testable)

1. The `se()` function contains zero occurrences of `innerHTML +=`.
2. The `se()` function uses `i.insertAdjacentHTML("beforeend", ...)` twice: once for the caption and once for the timestamp.
3. The `<img>` element's `load` event handler references the same DOM node that is in the live document (not a detached/orphaned copy).
4. `make check` passes 100% green.

## Verification / quality gates

- [ ] `make check` passes (linter + all tests green)
- [ ] No new warnings introduced
- [ ] Manual verification: search `se()` function body for `innerHTML +=` — zero occurrences
- [ ] Manual verification: `se()` contains two `insertAdjacentHTML("beforeend"` calls

## Edge cases

- `se()` called with no caption (`n` is falsy): only the timestamp `insertAdjacentHTML` executes. The `&&` short-circuit correctly skips the caption insertion. The `<img>` load handler is still preserved.
- `se()` called with empty string caption (`n = ""`): falsy, so caption is skipped — same as no caption. Correct behavior.

## Rollout / rollback

- Rollout: Deploy updated `app.js`
- Rollback: Revert the commit (restores `innerHTML +=` pattern)

## Notes / risks

- **Risk**: Line numbers shift if T1 was applied first (3 lines deleted from `Me()`). Developer must search for `function se(` to locate the correct code.
  - **Mitigation**: Implementation steps reference searchable code patterns, not just line numbers.
- **Risk**: The `n && i.insertAdjacentHTML(...)` expression — `insertAdjacentHTML` returns `undefined`, and `undefined` is falsy in JS. However, since `&&` only evaluates the right side when `n` is truthy, and we don't use the return value, this is correct.
  - **Mitigation**: The `&&` short-circuit pattern is idiomatic JS and matches other patterns in the codebase.
- **Risk**: Minified formatting must be preserved — no extra whitespace or line breaks.
  - **Mitigation**: Exact before/after strings provided.
