# Sprint: Non-Telethon API Full Cleanup

**Date:** 2026-02-24
**Goal:** Remove or privatize all 12 non-Telethon public methods on `ServerlessTelegramClient` / `ServerlessTelegramClientCore` so the public API surface matches Telethon's `TelegramClient` interface (plus two documented extensions: `api_calls` / `last_api_call`).

## Scope

### Methods to privatize (internal plumbing)
- `process_text_message` -> `_process_text_message`
- `process_file_message` -> `_process_file_message`
- `process_callback_query` -> `_process_callback_query`
- `pop_response` -> `_pop_response`

### Methods to privatize (payment)
- `simulate_stars_payment` -> `_simulate_stars_payment` (only called from RPC handler)

### Methods to replace with Telethon TL requests
- `get_bot_state` -> Demo UI uses `GetBotCommandsRequest` + `GetBotMenuButtonRequest` via `client(request)`
- `clear_bot_state` -> Add `ResetBotCommandsRequest` + `SetBotMenuButtonRequest` handlers to RPC

### Methods to remove
- `click_inline_button` on `ServerlessTelegramConversation` (replaced by `message.click()`)

### Methods KEPT as-is (documented extensions)
- `api_calls` (property)
- `last_api_call` (property)

## Out of Scope
- Changes to `proto_tg_bot` (separate repo). We ensure TL request equivalents exist so it can be updated later.

## Task Order and Dependencies

```
TASK_01  (Privatize internal plumbing: process_text_message, process_file_message, process_callback_query, pop_response)
   |
   v
TASK_02  (Privatize simulate_stars_payment, update demo UI pay_invoice to use TL request)
   |
   v
TASK_03  (Replace get_bot_state in demo UI with TL requests, privatize get_bot_state)
   |
   v
TASK_04  (Add ResetBotCommandsRequest + SetBotMenuButtonRequest to RPC, privatize clear_bot_state)
   |
   v
TASK_05  (Remove click_inline_button, update test to use message.click())
   |
   v
TASK_06  (Clean up vulture whitelist, README, final verification)
```

TASK_01 is the foundation — all internal Protocols depend on the renamed methods.

TASK_02 depends on TASK_01 because `pop_response` is renamed in TASK_01, and the demo UI `pay_invoice` route calls both `simulate_stars_payment` and `pop_response`.

TASK_03 depends on TASK_01 (demo UI routes reference `pop_response` which was renamed).

TASK_04 depends on TASK_03 (builds on the TL-request pattern established for bot state).

TASK_05 is independent of TASK_02-04 but ordered after them for clean sequencing.

TASK_06 depends on all previous tasks (final sweep).

## Key Constraints

- Files must not exceed 200 lines. Plan decomposition if needed.
- `make check` must be 100% green after each task.
- Each task produces a working, green codebase.
- `api_calls` and `last_api_call` are KEPT as documented extensions.
- `proto_tg_bot` changes are out of scope.

## Risks

| Risk | Mitigation |
|------|------------|
| Protocol changes break type checking | Update all Protocols (ConversationClient, CallbackClient, DemoClientProtocol) in the same task as the rename |
| Demo UI `routes.py` is 184 lines, changes could push it over 200 | Monitor line count; decompose if needed |
| `serverless_telethon_rpc.py` grows with new handlers | Currently 95 lines; adding 2 handlers is safe |
| Tests calling public methods need `_` prefix | Straightforward rename; tests testing internals via `_` methods is acceptable |

## Quality Gates

1. `make check` passes after every task (linter + tests).
2. No file exceeds 200 lines.
3. After TASK_06: zero non-Telethon public methods remain (except `api_calls` / `last_api_call`).

## Tasks

| ID | Title | Depends on |
|----|-------|------------|
| TASK_01 | Privatize internal plumbing methods | -- |
| TASK_02 | Privatize simulate_stars_payment, update demo UI | TASK_01 |
| TASK_03 | Replace get_bot_state with TL requests in demo UI | TASK_01 |
| TASK_04 | Add ResetBotCommandsRequest + SetBotMenuButtonRequest, privatize clear_bot_state | TASK_03 |
| TASK_05 | Remove click_inline_button from conversation | TASK_01 |
| TASK_06 | Clean up vulture whitelist, README, final verification | TASK_01--05 |
