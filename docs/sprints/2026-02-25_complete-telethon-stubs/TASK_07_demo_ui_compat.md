---
Task ID: `T7`
Title: `Fix 4 Demo UI Telethon-compatibility bugs in routes.py`
Depends on: T2
Parallelizable: yes, with T4, T5, T6
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Fix 4 confirmed Telethon-compatibility bugs in the Demo UI routes that would crash with a real Telethon client. After this task, all Demo UI routes use only standard Telethon public API patterns — no private method calls, no dummy peer values, no incorrect return type assumptions. The routes must work with both `ServerlessTelegramClient` and a real `TelegramClient`.

## Context (contract mapping)

- Requirements: User-confirmed bugs — "I've confirmed all four Demo UI issues are REAL"
- Architecture: Demo UI should use standard Telethon patterns for portability

## Preconditions

- T2 completed: `ServerlessTelegramClientCore` has public `send_message` method (needed because the conversation pattern's `send_message` now delegates to `client.send_message` in real Telethon)
- `make check` is green after T2
- `routes.py` is exactly 200 lines (at limit — fixes require decomposition)

## Non-goals

- Adding new Demo UI features (edit/delete visual indicators)
- Frontend JS/CSS changes
- Making the Demo UI work against a live Telegram server (but fix the patterns so it could in theory)

## Touched surface (expected files / modules)

- `tg_auto_test/demo_ui/server/routes.py` (modify — extract handlers, fix bugs)
- `tg_auto_test/demo_ui/server/routes_interactive.py` (NEW — extracted route handlers for invoice, poll, callback)
- `tg_auto_test/demo_ui/server/demo_server.py` (modify — update `DemoClientProtocol` to add `get_input_entity`, remove implicit `_pop_response` dependency)
- `tests/unit/test_demo_server.py` (modify — update `test_poll_vote_endpoint` to not use `_pop_response`)
- `vulture_whitelist.py` (may need additions for new handler function names — defer to T8 if possible)

## Dependencies and sequencing notes

- Depends on T2 because the conversation pattern in the serverless client needs client-level `send_message` to exist (conversation's `send_message` delegates to `client.send_message` in real Telethon).
- Can run in parallel with T4, T5, T6 since those tasks touch `test_utils/` files while this touches `demo_ui/` files.

## Third-party / library research (mandatory for any external dependency)

- **Library**: Telethon `TelegramClient`
- **Key API behaviors (verified from Telethon source)**:

  **`Conversation` pattern**: In real Telethon, `Conversation.send_message()` delegates to `client.send_message(input_chat, ...)` and `conv.get_response()` awaits the next incoming message. This is the correct pattern for invoice payments and poll votes — send a trigger, wait for the bot's response.

  **`Message.click()` return type**: In real Telethon, `click(data=...)` for inline buttons sends a `GetBotCallbackAnswerRequest` and returns a `BotCallbackAnswer` object (which has `.message`, `.alert`, `.url` attributes — NOT a `Message` object). The bot may separately send an edited message or new message as a side effect, which must be captured via `conv.get_response()` or `conv.get_edit()`.

  **`get_input_entity(peer)`**: Resolves a peer identifier (username, ID, etc.) to an `InputPeer` TL object. Available on `ServerlessTelegramClient` (already returns `InputPeerUser(user_id=999_999, access_hash=0)`).

  **`InputPeerEmpty()`**: Only valid for "no peer" contexts. Passing it as a real peer in `SendVoteRequest` or `SendStarsFormRequest` will fail with real Telegram. Must use an actual resolved peer.

## Implementation steps (developer-facing)

### Step 1: Create `routes_interactive.py` — extract invoice, poll, callback handlers

Create `tg_auto_test/demo_ui/server/routes_interactive.py` with the fixed handler functions for the 3 problematic endpoints. This follows the same pattern as `upload_handlers.py` — standalone async functions that take `DemoServer` as a parameter.

```python
"""Interactive route handlers for invoice, poll vote, and callback endpoints."""
```

### Step 2: Fix Bug 1 — `/api/invoice/pay` uses `_pop_response()` (routes.py line 133)

**Current broken code** (routes.py lines 124-139):
```python
async def pay_invoice(req: InvoicePayRequest) -> MessageResponse:
    request = SendStarsFormRequest(
        form_id=req.message_id,
        invoice=InputInvoiceMessage(peer=InputPeerEmpty(), msg_id=req.message_id),
    )
    await demo_server.client(request)
    response = demo_server.client._pop_response()  # BUG: private method
    result = await serialize_message(response, demo_server.file_store)
    ...
```

**Fix**: The `SendStarsFormRequest` TL call triggers the bot to process a successful payment and send a response message. Instead of poking the private outbox, use the conversation pattern to capture the bot's response. The TL request still needs to be made (to trigger the payment processing in the serverless infrastructure), but the response comes via conversation.

**Also fixes Bug 4 partially**: Replace `InputPeerEmpty()` with the resolved peer from `get_input_entity`.

The fixed handler in `routes_interactive.py`:
```python
async def handle_pay_invoice(demo_server: "DemoServer", req: InvoicePayRequest) -> MessageResponse:
    peer = await demo_server.client.get_input_entity(demo_server.peer)
    request = SendStarsFormRequest(
        form_id=req.message_id,
        invoice=InputInvoiceMessage(peer=peer, msg_id=req.message_id),
    )
    await demo_server.client(request)
    # Bot processes payment and sends confirmation — pop via standard API
    response = demo_server.client._pop_response()
    return await serialize_message(response, demo_server.file_store)
```

**IMPORTANT DESIGN DECISION**: The `_pop_response()` pattern is actually how the serverless client works internally — after a TL request triggers bot processing, the response lands in `_outbox` and must be popped. The conversation pattern (`conv.send_message` + `conv.get_response`) works because `send_message` triggers processing and `get_response` pops from outbox. BUT for TL requests (invoice pay, poll vote), there is no equivalent "conversation send" — the trigger is the TL `__call__`. 

The real fix has two parts:
1. **For the protocol**: Add `_pop_response` to `DemoClientProtocol` as a proper part of the interface (not a private method), OR
2. **Refactor invoice/poll routes to use conversation pattern entirely**: Instead of calling the TL request directly, use the conversation to send a synthetic message that triggers the same bot behavior.

**Best approach**: Since `_pop_response` is a fundamental part of how the serverless infrastructure works (TL request → bot processes → response in outbox), make it a public method `pop_response()` on the client, and add it to `DemoClientProtocol`. This is cleaner than faking a conversation pattern for TL-initiated actions.

**Revised fix for invoice**:
- Rename `_pop_response` → `pop_response` on `ServerlessTelegramClientCore` (public API)
- Replace `InputPeerEmpty()` with resolved peer: `await demo_server.client.get_input_entity(demo_server.peer)`
- Update route to call `demo_server.client.pop_response()` (no underscore)

### Step 3: Fix Bug 2 — `/api/poll/vote` uses `_pop_response()` (routes.py line 191)

**Same pattern as Bug 1.** Also has Bug 4 (`InputPeerEmpty()` on line 182).

**Fix**:
- Replace `demo_server.client._pop_response()` with `demo_server.client.pop_response()`
- Replace `InputPeerEmpty()` with `await demo_server.client.get_input_entity(demo_server.peer)`

### Step 4: Fix Bug 3 — `/api/callback` assumes `click()` returns Message (routes.py line 149)

**Current broken code** (routes.py lines 141-155):
```python
async def handle_callback(req: CallbackRequest) -> MessageResponse:
    msg = await demo_server.client.get_messages(demo_server.peer, ids=req.message_id)
    if not msg:
        raise HTTPException(status_code=404, detail=...)
    response = await msg.click(data=req.data.encode())  # Returns BotCallbackAnswer in real Telethon!
    result = await serialize_message(response, demo_server.file_store)
    ...
```

**In real Telethon**, `msg.click(data=...)` sends a `GetBotCallbackAnswerRequest` and returns `BotCallbackAnswer`. The bot's actual response message (edit or new message) is a side effect. In our `ServerlessTelegramClient`, `click()` delegates to `_process_callback_query` which processes the update and returns the response `ServerlessMessage` — so our click returns a Message, but real Telethon's returns `BotCallbackAnswer`.

**Fix**: After `click()`, use `pop_response()` to get the actual bot response message. The `click()` return value should be ignored for serialization purposes. In the serverless client, `click()` already processes the callback and the response is in the outbox (via `handle_click_wrapper`). BUT `handle_click_wrapper` currently pops from the outbox itself (line 106-107 in file_processing_utils.py) and returns the result directly. So in the serverless case, `click()` already returns the right thing.

**Revised analysis**: The real issue is that `ServerlessTelegramClient.click()` returns a `ServerlessMessage` while real Telethon returns `BotCallbackAnswer`. The fix should make the route work with both:
- Call `msg.click(data=req.data.encode())`
- If the result has `.text` attribute (our ServerlessMessage), use it directly
- Otherwise (BotCallbackAnswer from real Telethon), use `pop_response()` to get the actual bot message

**Simplest correct fix**: Use `pop_response()` after click, since that's where the bot's response message is in both cases. In the serverless client, `handle_click_wrapper` already puts the result there. Actually, looking at `handle_click_wrapper`:
```python
async def handle_click_wrapper(client, message_id, data):
    outbox_before = len(client._outbox)
    result = await client._process_callback_query(message_id, data)
    while len(client._outbox) > outbox_before:
        client._outbox.pop()  # Removes from outbox!
    return result
```
It **removes** responses from the outbox and returns the result directly. So `pop_response()` after `click()` would NOT work in the serverless case — the outbox was already drained.

**Correct fix**: The route should continue using `click()` return value for the serverless case, but acknowledge that real Telethon compatibility requires a different approach. Since this is a testing library (not meant for real Telethon), the pragmatic fix is:
1. Keep using `click()` return value
2. Add a type check: if it has a `.text` attribute or is a `ServerlessMessage`, serialize it
3. Otherwise, it's a `BotCallbackAnswer` and we should handle that (but this won't happen in our serverless context)

**Even simpler**: The callback route already works correctly with our serverless client. The "bug" is about theoretical real-Telethon compatibility. Since the whole Demo UI is designed for `ServerlessTelegramClient`, the pragmatic fix is to document this limitation and leave the route as-is, OR restructure to use conversation pattern.

**Final decision**: Use the conversation pattern for the callback route — this is universally correct:
```python
async with demo_server.client.conversation(demo_server.peer, timeout=demo_server.timeout) as conv:
    # Send callback query through the client
    msg = await demo_server.client.get_messages(demo_server.peer, ids=req.message_id)
    await msg.click(data=req.data.encode())
    response = await conv.get_response()
```
BUT this won't work because `click()` bypasses the conversation's message tracking. The conversation expects messages sent via `conv.send_message()`.

**Actually correct approach**: Since `click()` in our serverless client calls `_process_callback_query` which adds to `_outbox`, and `conv.get_response()` calls `_pop_response()` which reads from `_outbox`, we can wrap in conversation:
```python
async with demo_server.client.conversation(demo_server.peer, timeout=demo_server.timeout) as conv:
    msg = await demo_server.client.get_messages(demo_server.peer, ids=req.message_id)
    await msg.click(data=req.data.encode())
    response = await conv.get_response()
```
Wait — `handle_click_wrapper` POPS from outbox. So after click returns, the outbox is empty. `conv.get_response()` would fail with "No pending response."

**Root cause in handle_click_wrapper**: It intentionally drains the outbox and returns the result. This is the correct serverless behavior for `msg.click()` (returns the response directly). The issue is that the route treats this return value as a Message, which is correct for serverless but not for real Telethon.

**THE RIGHT FIX**: For the callback route specifically, the response from `click()` IS the bot's response in serverless mode. The real-Telethon incompatibility is in the return type (Message vs BotCallbackAnswer), not in the response content. Since this library is a testing library, keep using `click()` return value but make the code robust:

```python
click_result = await msg.click(data=req.data.encode())
# In serverless mode, click() returns the bot's response Message directly.
# In real Telethon, click() returns BotCallbackAnswer and the bot's
# response message arrives separately. Handle both:
if hasattr(click_result, 'text') and hasattr(click_result, 'id'):
    response = click_result
else:
    response = demo_server.client.pop_response()
```

This approach works with both backends and doesn't require restructuring `handle_click_wrapper`.

### Step 5: Fix Bug 4 — Dummy peer values (routes.py lines 66, 129, 182)

Three locations use dummy peers:

1. **Line 66**: `GetBotMenuButtonRequest(user_id=InputPeerUser(user_id=0, access_hash=0))`
   - Fix: Use `await demo_server.client.get_input_entity(demo_server.peer)` to resolve the peer
   - Note: `GetBotMenuButtonRequest` expects a `user_id` parameter that is an `InputUser` or `InputPeerUser`. Using the resolved peer is correct.

2. **Line 129**: `InputInvoiceMessage(peer=InputPeerEmpty(), msg_id=req.message_id)` — fixed in Step 2

3. **Line 182**: `SendVoteRequest(peer=InputPeerEmpty(), ...)` — fixed in Step 3

### Step 6: Make `_pop_response` public

In `serverless_telegram_client_core.py`:
- Rename `_pop_response` to `pop_response` (remove leading underscore)
- Update all internal callers:
  - `serverless_telegram_conversation.py` line 66: `self._client._pop_response()` → `self._client.pop_response()`
  - `ConversationClient` protocol in `serverless_telegram_conversation.py` line 21: `def _pop_response(self)` → `def pop_response(self)`

In `demo_server.py`:
- Add `pop_response` to `DemoClientProtocol`:
  ```python
  def pop_response(self) -> object:
      """Pop the next bot response from the outbox."""
      ...
  ```
- Add `get_input_entity` to `DemoClientProtocol`:
  ```python
  async def get_input_entity(self, peer: object) -> object:
      """Resolve peer to InputPeer."""
      ...
  ```

### Step 7: Extract handlers to `routes_interactive.py`

Move the invoice, poll vote, and callback route handlers into `routes_interactive.py`. Each becomes a standalone async function that takes the `DemoServer` instance. The route registration in `routes.py` calls through to these functions.

This follows the exact pattern of `upload_handlers.py`:
```python
# In routes.py:
@app.post("/api/invoice/pay")
async def pay_invoice(req: InvoicePayRequest) -> MessageResponse:
    result = await handle_pay_invoice(demo_server, req)
    if demo_server.on_action is not None:
        await demo_server.on_action("pay_stars", demo_server.client)
    return result
```

The `on_action` callback stays in `routes.py` (consistent with other routes).

### Step 8: Update `test_demo_server.py`

The `test_poll_vote_endpoint` test (lines 133-175) creates a `MockClient` with `_pop_response`. Update to use `pop_response` (public):

```python
def pop_response(self) -> ServerlessMessage:
    return self._response
```

Also add `get_input_entity` mock:
```python
async def get_input_entity(self, peer: object) -> object:
    from telethon.tl.types import InputPeerUser
    return InputPeerUser(user_id=999_999, access_hash=0)
```

### Step 9: Update all remaining `_pop_response` callers

Search for `_pop_response` across the codebase and update:
- `tests/unit/test_serverless_poll_answer.py` lines 82, 102: `client._pop_response()` — these are test files using the serverless client directly. Update to `client.pop_response()`.
- `tests/unit/test_serverless_client_stars_payments.py` lines 54, 86, 95, 154: same update.
- `file_processing_utils.py` line 111-115: `pop_client_response` function — this IS `_pop_response`. Update the function and callers.

### Step 10: Verify line counts and run `make check`

- `routes.py`: should drop from 200 to ~160 lines (3 handler bodies moved out)
- `routes_interactive.py`: should be ~80-100 lines
- `demo_server.py`: should be ~150 lines (2 new protocol methods)
- All files under 200 lines
- `make check` is 100% green

## Production safety constraints (mandatory)

N/A — testing library, no production resources.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: extraction follows existing `upload_handlers.py` pattern; `get_input_entity` already exists on `ServerlessTelegramClient`.
- **Correct file locations**: new file in `tg_auto_test/demo_ui/server/` following naming convention.
- **No regressions**: existing tests updated to match new API; `make check` green.
- **Follow UX/spec**: route behaviors unchanged — same inputs produce same outputs.

## Error handling + correctness rules (mandatory)

- All routes must use public API only — no `# noqa: SLF001` access to private attributes.
- `get_input_entity` must be awaited (it's async).
- Callback route must handle both `ServerlessMessage` and `BotCallbackAnswer` return types from `click()`.
- No silent fallbacks — if `pop_response()` fails, let the error propagate.

## Zero legacy tolerance rule (mandatory)

- `_pop_response` must not exist anywhere in Demo UI code after this task.
- `InputPeerEmpty()` and `InputPeerUser(user_id=0, access_hash=0)` must not exist in route files after this task.
- No dead code from old handler implementations.
- Old handler bodies fully removed from `routes.py` (replaced with delegation to `routes_interactive.py`).
- Remove `# noqa: SLF001` comments from routes that no longer access private attributes.

## Acceptance criteria (testable)

1. `grep -r "_pop_response" tg_auto_test/demo_ui/` returns zero matches.
2. `grep -r "InputPeerEmpty\|InputPeerUser(user_id=0" tg_auto_test/demo_ui/server/routes*.py` returns zero matches.
3. `_pop_response` renamed to `pop_response` in `ServerlessTelegramClientCore`.
4. `DemoClientProtocol` includes `pop_response` and `get_input_entity`.
5. `/api/invoice/pay` route uses `get_input_entity(peer)` for the `InputInvoiceMessage` peer.
6. `/api/poll/vote` route uses `get_input_entity(peer)` for the `SendVoteRequest` peer.
7. `/api/state` route uses `get_input_entity(peer)` for the `GetBotMenuButtonRequest`.
8. `/api/callback` route handles both `ServerlessMessage` and non-Message return types from `click()`.
9. `routes.py` under 200 lines.
10. `routes_interactive.py` under 200 lines.
11. `demo_server.py` under 200 lines.
12. `test_demo_server.py` `test_poll_vote_endpoint` passes without `_pop_response`.
13. `make check` is 100% green.

## Verification / quality gates

- [ ] `make check` passes
- [ ] All Demo UI tests pass
- [ ] `wc -l` on `routes.py`, `routes_interactive.py`, `demo_server.py` all < 200
- [ ] `grep -r "_pop_response" tg_auto_test/demo_ui/` returns nothing
- [ ] `grep -r "InputPeerEmpty\|InputPeerUser(user_id=0" tg_auto_test/demo_ui/server/routes*.py` returns nothing
- [ ] No `# noqa: SLF001` in Demo UI route files (for the fixed methods)

## Edge cases

- `get_input_entity` is already defined on `ServerlessTelegramClient` (returns `InputPeerUser(user_id=999_999, access_hash=0)` regardless of input). This works for the serverless case. For real Telethon, it resolves the peer properly.
- `pop_response()` on an empty outbox should raise `RuntimeError("No pending response")` — existing behavior preserved.
- Callback route: if `click()` returns an object without `.text` or `.id`, the fallback to `pop_response()` must work. In the serverless client, `handle_click_wrapper` drains the outbox and returns the message, so `pop_response()` would fail. The type check (`hasattr(click_result, 'text') and hasattr(click_result, 'id')`) correctly routes to direct use of the click result in this case.
- `vote_poll` route (routes.py line 175) uses `app.state.demo_server` instead of the closure `demo_server`. This should be unified to use the closure (consistent with all other routes). Fix as part of the extraction.

## Notes / risks

- **Risk**: Renaming `_pop_response` to `pop_response` touches many files across test_utils and tests.
  - **Mitigation**: Systematic search-and-replace. The method is only used in ~8 places. All callers updated in Step 9.

- **Risk**: Adding `get_input_entity` and `pop_response` to `DemoClientProtocol` may break existing mock clients in tests.
  - **Mitigation**: `DemoClientProtocol` is a typing `Protocol` — it uses structural typing. Existing mock clients that don't implement these new methods will cause type errors but not runtime errors (protocol checking is static). The `test_demo_server.py` MockClient is the only one that needs updating.

- **Risk**: The `vote_poll` handler references `app.state.demo_server` (line 175) instead of the closure `demo_server`. This is a latent bug — the closure variable and app state should always point to the same object, but it's inconsistent.
  - **Mitigation**: Fix as part of extraction — use the `demo_server` parameter consistently.
