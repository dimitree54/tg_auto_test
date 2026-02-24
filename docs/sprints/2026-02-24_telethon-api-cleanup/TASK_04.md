# TASK_04 — Add ResetBotCommandsRequest + SetBotMenuButtonRequest handlers, privatize clear_bot_state

**Dependencies:** TASK_03 (TL request pattern for bot state established; `_scope_key_from_telethon` may have been extended)

## Objective

Add handlers for `ResetBotCommandsRequest` and `SetBotMenuButtonRequest` to the Telethon RPC layer so that consumers (like `proto_tg_bot`) can clear bot state via Telethon TL requests. Then privatize `clear_bot_state` to `_clear_bot_state`.

## Files to modify

| File | Change |
|------|--------|
| `tg_auto_test/test_utils/serverless_telethon_rpc.py` | Add `functions.bots.ResetBotCommandsRequest` and `functions.bots.SetBotMenuButtonRequest` to the `TelethonRequest` union type and `TelethonResponse` union type. Add handler branches in `handle_telethon_request` for both. |
| `tg_auto_test/test_utils/serverless_telegram_client_core.py` | Rename `clear_bot_state` -> `_clear_bot_state`. |
| `vulture_whitelist.py` | Remove `clear_bot_state` entry (method is now private; no longer needs whitelisting). |
| `tests/` (new or existing test file) | Add tests for the new TL request handlers: verify `ResetBotCommandsRequest` clears commands, verify `SetBotMenuButtonRequest` resets menu button. |

## Requirements

1. `ResetBotCommandsRequest` handler must clear bot commands for the given scope. Implementation: call `client._clear_bot_state()` or directly use `client.request` to delete scoped commands and reset menu button. Preferred approach: delegate to the underlying PTB stub, similar to how `GetBotCommandsRequest` reads from `client.request.get_scoped_commands()`.
2. `SetBotMenuButtonRequest` handler must set the menu button. Implementation: update `client.request._menu_button` based on the request's `button` field.
3. Both new request types must be added to the `TelethonRequest` and `TelethonResponse` union types.
4. `clear_bot_state` must not exist as a public method after this task.

## Implementation detail

### ResetBotCommandsRequest handler
```python
if isinstance(request, functions.bots.ResetBotCommandsRequest):
    key = _scope_key_from_telethon(request.scope)
    client.request._scoped_commands.pop(key, None)
    return True  # Telethon returns Bool
```

### SetBotMenuButtonRequest handler
```python
if isinstance(request, functions.bots.SetBotMenuButtonRequest):
    if isinstance(request.button, types.BotMenuButtonDefault):
        client.request._menu_button = None
    elif isinstance(request.button, types.BotMenuButtonCommands):
        client.request._menu_button = {"type": "commands"}
    else:
        client.request._menu_button = None
    return True  # Telethon returns Bool
```

### TelethonResponse update
Add `bool` to the `TelethonResponse` union since both new handlers return `True`.

## Acceptance Criteria

1. `make check` passes.
2. `ResetBotCommandsRequest` clears commands for the given scope when called via `client(request)`.
3. `SetBotMenuButtonRequest` updates the menu button when called via `client(request)`.
4. No public `clear_bot_state` method exists.
5. `clear_bot_state` is removed from `vulture_whitelist.py`.
6. `serverless_telethon_rpc.py` does not exceed 200 lines (currently 95 lines; adding ~20 lines for handlers is safe).
7. Tests exist verifying both new TL request handlers.

## Risks

- **`_scope_key_from_telethon` may not handle `ResetBotCommandsRequest.scope`**: Verify that the scope type used by `ResetBotCommandsRequest` is already handled. The function currently handles `BotCommandScopePeer` and `BotCommandScopeDefault`. May need to add `BotCommandScopePeerUser` if TASK_03 didn't already.
- **`TelethonResponse` union**: Adding `bool` to the union is a type change. Ensure it doesn't break existing callers.
- **proto_tg_bot compatibility**: After this task, `proto_tg_bot` can replace `client.clear_bot_state()` with `client(ResetBotCommandsRequest(...))` + `client(SetBotMenuButtonRequest(...))`. This is out of scope but the capability is now available.
