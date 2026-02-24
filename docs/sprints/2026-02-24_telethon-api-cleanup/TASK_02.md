# TASK_02 — Privatize simulate_stars_payment, update demo UI

**Dependencies:** TASK_01 (pop_response is already renamed to _pop_response)

## Objective

Make `simulate_stars_payment` private (`_simulate_stars_payment`) on `ServerlessTelegramClient`. Update the demo UI `pay_invoice` route to use the Telethon `SendStarsFormRequest` TL request via `client(request)` instead of calling `simulate_stars_payment` directly.

## Files to modify

| File | Change |
|------|--------|
| `tg_auto_test/test_utils/serverless_telegram_client.py` | Rename `simulate_stars_payment` -> `_simulate_stars_payment`. |
| `tg_auto_test/test_utils/serverless_telethon_rpc.py` | Update the `SendStarsFormRequest` handler: `client.simulate_stars_payment(...)` -> `client._simulate_stars_payment(...)`. |
| `tg_auto_test/demo_ui/server/routes.py` | Rewrite `pay_invoice` route to use `SendStarsFormRequest` via `await demo_server.client(request)` instead of `demo_server.client.simulate_stars_payment(...)`. Get the response via `demo_server.client._pop_response()`. Add `from telethon.tl.functions.payments import SendStarsFormRequest` and `from telethon.tl.types import InputInvoiceMessage, InputPeerEmpty` imports. |
| `tg_auto_test/demo_ui/server/demo_server.py` | Remove `simulate_stars_payment` from `DemoClientProtocol` (no longer called by routes). |
| `tests/unit/test_serverless_client_stars_payments.py` | Update all `client.simulate_stars_payment(...)` calls to use `SendStarsFormRequest` via `await client(request)` instead. This makes the tests exercise the Telethon-native path. |
| `tests/unit/test_demo_server.py` | Remove `simulate_stars_payment` from `MockClient`. Add `__call__` mock if not already present. |

## Requirements

1. `simulate_stars_payment` must not exist as a public method after this task.
2. The demo UI `pay_invoice` route must construct a `SendStarsFormRequest` with `InputInvoiceMessage(peer=InputPeerEmpty(), msg_id=req.message_id)` and call `await demo_server.client(request)`.
3. After calling `SendStarsFormRequest`, the route gets the payment confirmation response via `demo_server.client._pop_response()`.
4. The RPC handler in `serverless_telethon_rpc.py` calls `client._simulate_stars_payment(...)`.
5. Star payment tests must be updated to use the Telethon-native `SendStarsFormRequest` pattern.

## Acceptance Criteria

1. `make check` passes.
2. No public `simulate_stars_payment` method exists.
3. `pay_invoice` route uses `SendStarsFormRequest` via `client(request)`.
4. All star payment tests pass using the Telethon-native API.
5. No file exceeds 200 lines.

## Risks

- **Demo UI route complexity**: The `pay_invoice` route needs to construct Telethon TL types. This adds import complexity but is straightforward.
- **`routes.py` line count**: Currently 184 lines. Adding imports may push it close to 200. Monitor carefully; if it exceeds the limit, decompose the payment route into a helper module (similar to `upload_handlers.py`).
- **Test refactoring**: Star payment tests change from `client.simulate_stars_payment()` to `client(SendStarsFormRequest(...))` + `client._pop_response()`. The test semantics are identical but the API surface is Telethon-native.
