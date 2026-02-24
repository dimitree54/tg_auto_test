# TASK_01 — Privatize internal plumbing methods

**Dependencies:** None

## Objective

Rename the four internal plumbing methods from public to private (underscore-prefixed) and update all internal Protocols, callers, and tests that reference them.

Methods to rename on `ServerlessTelegramClientCore`:
- `process_text_message` -> `_process_text_message`
- `process_file_message` -> `_process_file_message`
- `process_callback_query` -> `_process_callback_query`
- `pop_response` -> `_pop_response`

## Files to modify

| File | Change |
|------|--------|
| `tg_auto_test/test_utils/serverless_telegram_client_core.py` | Rename the four methods to `_`-prefixed. Update the internal `_handle_click` call to `self._process_callback_query`. |
| `tg_auto_test/test_utils/serverless_telegram_conversation.py` | Update `ConversationClient` Protocol: rename all four method signatures to `_`-prefixed. Update `ServerlessTelegramConversation` method bodies to call `_`-prefixed names on `self._client`. |
| `tg_auto_test/test_utils/telethon_compatible_message.py` | Update `CallbackClient` Protocol: rename `process_callback_query` to `_process_callback_query`. Update `TelethonCompatibleMessage.click()` to call `self._client._process_callback_query`. |
| `tg_auto_test/demo_ui/server/routes.py` | Update `pay_invoice` route: `demo_server.client.pop_response()` -> `demo_server.client._pop_response()`. Update `vote_poll` route: `demo_server.client.pop_response()` -> `demo_server.client._pop_response()`. |
| `tg_auto_test/demo_ui/server/demo_server.py` | Update `DemoClientProtocol`: rename `pop_response` to `_pop_response`. |
| `tests/unit/test_demo_server.py` | Update `MockClient.pop_response` -> `_pop_response`. Update `MockClient.__init__` references. |
| `tests/unit/test_serverless_poll_answer.py` | Update `client.pop_response()` -> `client._pop_response()` (2 occurrences). |
| `tests/unit/test_serverless_client_stars_payments.py` | No changes needed — these tests use `client.simulate_stars_payment()` and `conv.get_response()`, not the renamed methods directly. |

## Requirements

1. Rename all four methods consistently across definitions, Protocols, and call sites.
2. Protocol definitions must use the `_`-prefixed names so type checking remains valid.
3. The `click_inline_button` method (removed in TASK_05) still calls `_process_callback_query` — update its call site in this task.
4. All tests that directly call these methods must use the new `_`-prefixed names.

## Acceptance Criteria

1. `make check` passes (linter + all tests green).
2. No public methods named `process_text_message`, `process_file_message`, `process_callback_query`, or `pop_response` exist anywhere in the library.
3. All internal callers and Protocols use the `_`-prefixed names.
4. No file exceeds 200 lines.

## Risks

- **Protocol changes could break type checking**: Mitigated by updating all Protocols in the same task.
- **Many call sites to update**: grep thoroughly for all four method names before marking complete.
- **`noqa: SLF001` annotations may be needed**: Tests and internal callers accessing `_`-prefixed methods on other objects may need `# noqa: SLF001` suppression. The `_handle_click` already uses this pattern.
