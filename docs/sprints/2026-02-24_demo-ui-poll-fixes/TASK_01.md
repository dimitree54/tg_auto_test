# TASK_01 — Fix poll event handlers destroyed by innerHTML += and remove dead Me()

---
Task ID: `T1`
Title: Fix poll event handlers destroyed by `innerHTML +=` and remove dead `Me()`
Depends on: —
Parallelizable: yes (with T2 and T3 — different functions/files)
Owner: Developer
Status: `planned`
---

## Goal / value

Poll option buttons must retain their `.onclick` handlers after the poll message is rendered. Currently, `innerHTML +=` in `Pe()` serializes and re-parses the entire container, destroying all event listeners on child elements. Additionally, `Me()` is a buggy duplicate of `P()` (passes a `Date` object to `I()` which expects seconds) — it must be removed entirely.

## Context (contract mapping)

- Requirements: N/A (bugfix)
- Architecture: N/A (bugfix)
- Related sprints: `2026-02-23_poll-support` (introduced `Pe()` and `Me()`)

## Preconditions

- `make check` passes on the current codebase (baseline green)

## Non-goals

- Reformatting or prettifying `app.js`
- Changing any function other than `Pe()` and deleting `Me()`

## Touched surface (expected files / modules)

- `tg_auto_test/demo_ui/server/static/ui/app.js` — functions `Me()` (lines 353-355) and `Pe()` (lines 364-378)

## Dependencies and sequencing notes

- No dependencies. `Pe()` and `Me()` are only called from this code path.
- Can run in parallel with T2 (different function `se()`) and T3 (different file `app.css`).
- Executed first by convention.

## Third-party / library research (mandatory for any external dependency)

No third-party libraries involved. The fix uses standard DOM API:

- **API**: `Element.insertAdjacentHTML(position, text)`
  - **MDN documentation**: https://developer.mozilla.org/en-US/docs/Web/API/Element/insertAdjacentHTML
  - Position `"beforeend"` inserts HTML just inside the element, after its last child — equivalent to `innerHTML +=` but without re-parsing existing children.
  - Browser support: all modern browsers (Chrome 1+, Firefox 8+, Safari 4+).
  - **Key advantage over `innerHTML +=`**: does not serialize and re-parse existing DOM nodes, so event listeners on existing children are preserved.

## Implementation steps (developer-facing)

### Step 1: Delete the `Me()` function (lines 353-355)

Remove these exact 3 lines from `app.js`:

```javascript
function Me() {
  return `<span class="meta">${I(/* @__PURE__ */ new Date())}</span>`;
}
```

**Why**: `Me()` calls `I(new Date())` but `I()` (line 289) expects a number (seconds for audio duration formatting), not a `Date` object. The `Date` object coerces to a large millisecond timestamp, producing garbled output like "30437542:24". The correct timestamp function is `P()` (line 399) which calls `W()` to format hours:minutes. After removing `Me()`, all callers use `P()`.

### Step 2: Fix `Pe()` to use `insertAdjacentHTML` and `P()`

On line 377 of `app.js`, replace:

```javascript
  s.innerHTML += Me(), n.messagesEl.appendChild(s), Se();
```

with:

```javascript
  s.insertAdjacentHTML("beforeend", P()), n.messagesEl.appendChild(s), Se();
```

**What changes**:
1. `Me()` → `P()` — uses the correct timestamp function
2. `s.innerHTML +=` → `s.insertAdjacentHTML("beforeend", ...)` — appends HTML without destroying existing DOM nodes and their event listeners

**Why `insertAdjacentHTML`**: The `innerHTML +=` pattern serializes the element's current DOM tree to HTML, concatenates the new string, and re-parses the entire result. This creates new DOM nodes, destroying any `.onclick` handlers that were set programmatically on the poll option buttons (set on line 374 via `r.onclick = () => He(...)`).

### Step 3: Verify no other callers of `Me()` exist

Search `app.js` for any other references to `Me()`. There should be none — `Me()` was only called on line 377 (now replaced with `P()`).

### Step 4: Run `make check`

```bash
make check
```

Must be 100% green.

## Production safety constraints (mandatory)

- **Database operations**: None. This is a static JavaScript file change.
- **Resource isolation**: The development `app.js` is in a separate directory from the production instance. No shared resources are affected.
- **Migration preparation**: N/A.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: Reuses existing `P()` function instead of creating a new one.
- **Correct file locations**: Edit is to the existing `app.js` in its current location.
- **No regressions**: `insertAdjacentHTML("beforeend", ...)` is semantically equivalent to `innerHTML +=` for appending, but preserves event listeners. No behavioral regression.
- **Follow UX/spec**: Poll buttons will now work as intended (onclick handlers preserved).

## Error handling + correctness rules (mandatory)

- No error handling changes in this task.
- The fix eliminates a silent failure (onclick handlers silently destroyed by DOM re-parsing).

## Zero legacy tolerance rule (mandatory)

- `Me()` is removed entirely — no dead code left behind.
- No "backward compatibility" wrapper or alias for `Me()`.

## Acceptance criteria (testable)

1. The `Me()` function (previously lines 353-355) does not exist in `app.js`.
2. `Pe()` calls `P()` instead of `Me()` for the timestamp span.
3. `Pe()` uses `s.insertAdjacentHTML("beforeend", P())` instead of `s.innerHTML += ...`.
4. `make check` passes 100% green.
5. No other references to `Me` exist in `app.js` (no dangling calls).

## Verification / quality gates

- [ ] `make check` passes (linter + all tests green)
- [ ] No new warnings introduced
- [ ] Manual verification: search `app.js` for `Me(` — zero occurrences
- [ ] Manual verification: line 377 (or equivalent after deletion shifts lines) contains `insertAdjacentHTML("beforeend", P())`

## Edge cases

- If `Pe()` is called with no `poll_options` (only `poll_question`), the `innerHTML +=` still runs for the timestamp. The fix handles this correctly — `insertAdjacentHTML` works regardless of whether child buttons exist.

## Rollout / rollback

- Rollout: Deploy updated `app.js`
- Rollback: Revert the commit (restores `Me()` and `innerHTML +=`)

## Notes / risks

- **Risk**: Line numbers shift after deleting `Me()` (3 lines removed). The developer should locate `Pe()` by searching for `function Pe(` rather than relying on absolute line numbers.
  - **Mitigation**: Implementation steps reference both line numbers AND searchable code patterns.
- **Risk**: Minified formatting — the replacement string must exactly match the surrounding code style (no extra spaces, no line breaks).
  - **Mitigation**: Exact before/after strings provided in implementation steps.
