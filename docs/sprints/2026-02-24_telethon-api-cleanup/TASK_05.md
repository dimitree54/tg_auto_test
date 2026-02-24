# TASK_05 — Remove click_inline_button from conversation

**Dependencies:** TASK_01 (process_callback_query renamed to _process_callback_query)

## Objective

Remove the `click_inline_button` method from `ServerlessTelegramConversation`. Update the one test that uses it to use the Telethon-native `message.click()` pattern instead.

## Files to modify

| File | Change |
|------|--------|
| `tg_auto_test/test_utils/serverless_telegram_conversation.py` | Remove the `click_inline_button` method entirely. |
| `tests/unit/test_serverless_client_callbacks.py` | Rewrite `test_click_via_conversation` to use `get_messages()` + `message.click()` instead of `conv.click_inline_button()`. |
| `vulture_whitelist.py` | Remove `click_inline_button` entry. |
| `README.md` | Remove the `click_inline_button` reference from the API documentation. |

## Requirements

1. `click_inline_button` must not exist anywhere in the library after this task.
2. The test `test_click_via_conversation` must be rewritten to:
   - Send `/inline` and get the response with buttons.
   - Use `await client.get_messages("test_bot", ids=msg_with_buttons.id)` to get a `TelethonCompatibleMessage`.
   - Call `await message.click(data=b"opt_a")` on the result.
   - Assert the response text.
3. This matches how real Telethon users click buttons: they get a message object and call `.click()` on it.

## Updated test pattern

```python
async def test_click_via_get_messages() -> None:
    """Test clicking buttons via get_messages + message.click() (Telethon pattern)."""
    client = ServerlessTelegramClient(build_application=build_test_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            await conv.send_message("/inline")
            msg_with_buttons = await conv.get_response()

            # Use Telethon pattern: get message, then click
            message = await client.get_messages("test_bot", ids=msg_with_buttons.id)
            response_msg = await message.click(data=b"opt_a")

            assert response_msg.text == "You chose: opt_a"
    finally:
        await client.disconnect()
```

## Acceptance Criteria

1. `make check` passes.
2. `click_inline_button` does not exist in any source file.
3. `click_inline_button` is removed from `vulture_whitelist.py`.
4. `click_inline_button` is removed from `README.md`.
5. The replacement test uses the `get_messages()` + `message.click()` pattern.
6. No file exceeds 200 lines.

## Risks

- **Minimal risk**: This is a straightforward removal. Only one test uses `click_inline_button` directly. The other callback tests already use `message.click()`.
- **README update**: Ensure the documentation accurately reflects the supported API after removal.
