---
Task ID: `T7`
Title: `Remove pop_response() from Demo UI routes_interactive.py`
Depends on: T4
Parallelizable: yes, with T5 and T6
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Eliminate all 3 `pop_response()` calls from `routes_interactive.py`. Real `TelegramClient` doesn't have `pop_response()` — these routes must work through standard Telethon patterns only. After this task, the Demo UI's interactive routes (pay invoice, callback, poll vote) use the conversation pattern or direct internal processing instead of `pop_response()`.

## Context (contract mapping)

- Requirements: User's GAP 3 — "`pop_response()` in Demo UI"
- Architecture: Demo UI routes should use standard Telethon patterns so they are portable to real Telethon clients

## Preconditions

- T4 complete (client stubs added — ensures the client interface is stable before modifying routes)
- `make check` is green

## Non-goals

- Making Demo UI work with a live Telegram server
- Changing the public HTTP API of the Demo UI
- Removing `pop_response()` from `ServerlessTelegramClientCore` itself (it may still be used internally or by tests)

## Touched surface (expected files / modules)

- `tg_auto_test/demo_ui/server/routes_interactive.py` (MODIFY — replace 3 `pop_response()` calls)
- `tg_auto_test/demo_ui/server/demo_server.py` (MODIFY — remove `pop_response` from `DemoClientProtocol` if no longer needed by routes)
- `tests/unit/test_demo_server.py` (MODIFY — update mocks if `pop_response` was used in test setup)
- `tests/unit/test_demo_server_api_state.py` (CHECK — may need updates)

## Dependencies and sequencing notes

- Depends on T4 because the client interface must be stable (stubs added) before changing how routes interact with the client.
- Can run in parallel with T5 and T6 since it touches only Demo UI files.

## Third-party / library research

- **Framework**: FastAPI (current version in `uv.lock`)
- **Pattern**: The existing `routes.py` uses the conversation pattern for text/file messages:
  ```python
  async with demo_server.client.conversation(demo_server.peer, timeout=demo_server.timeout) as conv:
      response = await conv.send_message(text)
  ```
  This is the target pattern for interactive routes too.

## Implementation steps (developer-facing)

1. **Analyze the 3 `pop_response()` call sites** in `routes_interactive.py`:

   **Site 1 — `handle_pay_invoice` (line 30)**:
   ```python
   await demo_server.client(request)
   response = demo_server.client.pop_response()
   ```
   The `client(request)` call invokes `handle_telethon_request` which processes the `SendStarsFormRequest`. The response is pushed to the outbox and then popped. Fix: use `_pop_response()` (the private method that the public `pop_response()` delegates to), OR restructure to use the conversation pattern, OR capture the response from the `__call__` result.

   **Site 2 — `handle_callback` (line 45)**:
   ```python
   if hasattr(click_result, "text") and hasattr(click_result, "id"):
       response = click_result
   else:
       response = demo_server.client.pop_response()
   ```
   The fallback `pop_response()` handles the case where `click()` returns something other than a full message. Fix: After `click()`, the bot's response should already be in the outbox — use `_pop_response()` or restructure.

   **Site 3 — `handle_poll_vote` (line 67)**:
   ```python
   await demo_server.client(vote_request)
   response = demo_server.client.pop_response()
   ```
   Same pattern as invoice. The `__call__` processes the vote request, response goes to outbox.

2. **Choose the replacement pattern**:
   The cleanest fix is to change `ServerlessTelegramClient.__call__` (in `serverless_telethon_rpc.py`) to return the bot response directly instead of pushing to outbox. However, that may be a larger change. The simpler fix:
   - Use `_pop_response()` (the private method) which is a legitimate internal API for our fake client.
   - OR wrap the TL request execution in a conversation pattern.
   - OR modify the `__call__` to return the processed response.

   **Recommended approach**: Refactor `routes_interactive.py` to use the conversation pattern for invoice/poll, and fix the callback handler to always use the click result. The conversation's `get_response()` internally calls `pop_response()`, which is the Telethon-compatible way. This way the routes don't call `pop_response()` directly.

   ```python
   # Invoice: use conversation to get response after TL request
   async with demo_server.client.conversation(demo_server.peer, timeout=demo_server.timeout) as conv:
       await demo_server.client(request)
       response = await conv.get_response()

   # Poll vote: same pattern
   async with demo_server.client.conversation(demo_server.peer, timeout=demo_server.timeout) as conv:
       await demo_server.client(vote_request)
       response = await conv.get_response()

   # Callback: click() already returns the response message
   click_result = await msg.click(data=req.data.encode())
   response = click_result  # Always a ServerlessMessage in our implementation
   ```

3. **Update `routes_interactive.py`**: Replace all 3 `pop_response()` calls with the chosen pattern. Ensure the file stays under 200 lines (currently 70 lines, changes should keep it under 80).

4. **Update `demo_server.py` — `DemoClientProtocol`**:
   - Remove `pop_response` from the protocol if no routes call it anymore.
   - Check if any other code depends on `pop_response` being in the protocol.

5. **Update tests**:
   - Check `tests/unit/test_demo_server.py` — if any test mocks `pop_response()`, update to use the new pattern.
   - Check `tests/unit/test_demo_server_api_state.py` — same.

6. **Run `make check`** — must be 100% green.

## Production safety constraints (mandatory)

N/A — testing library, no production resources.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: Using existing conversation pattern already established in `routes.py`.
- **Correct file locations**: Modifying existing files in-place.
- **No regressions**: Demo UI tests updated to match new behavior. HTTP API unchanged.

## Error handling + correctness rules (mandatory)

- Do not swallow errors from `conv.get_response()`.
- If conversation pattern fails, let the exception propagate to FastAPI's error handler.
- Do not add silent fallbacks.

## Zero legacy tolerance rule (mandatory)

- Remove `pop_response` from `DemoClientProtocol` if no longer used by routes.
- Remove any dead code related to the old `pop_response` pattern in routes.
- Do NOT remove `pop_response()` or `_pop_response()` from `ServerlessTelegramClientCore` itself — it's still used internally by conversation's `get_response()`.

## Acceptance criteria (testable)

1. `routes_interactive.py` contains zero `pop_response()` calls (grep confirms).
2. Demo UI interactive routes (invoice, callback, poll) still function correctly.
3. `DemoClientProtocol` does not expose `pop_response` (if no other consumer needs it).
4. All Demo UI tests pass.
5. `make check` is 100% green.

## Verification / quality gates

- [ ] `make check` passes
- [ ] `grep -r "pop_response" tg_auto_test/demo_ui/` returns zero hits in route files
- [ ] `uv run pytest tests/unit/test_demo_server.py -v` — all pass
- [ ] `uv run pytest tests/unit/test_demo_server_api_state.py -v` — all pass
- [ ] No new warnings introduced
- [ ] `routes_interactive.py` under 200 lines

## Edge cases

- The `handle_callback` path where `click_result` doesn't have `text` and `id` attributes — after this change, should we still handle that case? In our implementation, `click()` always returns `ServerlessMessage`. Remove the type-check fallback and always use `click_result` directly.
- If `conv.get_response()` is called when the outbox is empty (e.g., TL request didn't produce a response), it will fail. Ensure the invoice and poll request handlers always produce a response before `get_response()` is called.

## Notes / risks

- **Risk**: The conversation pattern for invoice/poll may behave differently than direct `pop_response()` if the conversation context manager has side effects.
  - **Mitigation**: The `ServerlessTelegramConversation.__aenter__` and `__aexit__` are no-ops in our implementation. The conversation's `get_response()` calls `self._client.pop_response()` internally, so the behavior is equivalent.
- **Risk**: Removing `pop_response` from `DemoClientProtocol` may break external consumers who implement the protocol.
  - **Mitigation**: The protocol is internal to the demo UI. If external consumers exist, they should use the conversation pattern instead.
