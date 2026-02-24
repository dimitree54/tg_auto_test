# TASK_03 — Replace get_bot_state with TL requests in demo UI, privatize

**Dependencies:** TASK_01 (pop_response renamed to _pop_response; demo UI routes already updated for that)

## Objective

Replace the demo UI's direct call to `client.get_bot_state()` with Telethon TL requests (`GetBotCommandsRequest` + `GetBotMenuButtonRequest`) via `client(request)`. Then privatize `get_bot_state` to `_get_bot_state` on `ServerlessTelegramClientCore`.

## Files to modify

| File | Change |
|------|--------|
| `tg_auto_test/demo_ui/server/routes.py` | Rewrite `get_state` route to use `GetBotCommandsRequest` and `GetBotMenuButtonRequest` via `await demo_server.client(request)`. Construct `BotStateResponse` from the TL response objects. Add imports for `GetBotCommandsRequest`, `GetBotMenuButtonRequest`, `BotCommandScopePeerUser`, `InputPeerUser`, `BotMenuButtonCommands`. |
| `tg_auto_test/demo_ui/server/demo_server.py` | Remove `get_bot_state` from `DemoClientProtocol`. |
| `tg_auto_test/test_utils/serverless_telegram_client_core.py` | Rename `get_bot_state` -> `_get_bot_state`. |
| `tests/unit/test_demo_server_api_state.py` | Update tests: `client.get_bot_state()` -> `client._get_bot_state()`. Update mock client tests to verify the new TL-request-based route pattern. |
| `tests/unit/test_demo_server.py` | Remove `get_bot_state` from `MockClient` (no longer in DemoClientProtocol). |

## Requirements

1. The `get_state` route must call `GetBotCommandsRequest` with the appropriate scope and `GetBotMenuButtonRequest` via `await demo_server.client(request)`.
2. The route must convert the TL response (`list[BotCommand]` and `BotMenuButtonCommands | BotMenuButtonDefault`) into the existing `BotStateResponse` model.
3. `get_bot_state` must not exist as a public method after this task.
4. The `_get_bot_state` private method is kept for internal use (it wraps PTB directly); TL requests go through the RPC layer.

## Implementation detail for the route

The `get_state` route currently does:
```python
bot_state = await demo_server.client.get_bot_state()
```

Replace with:
```python
from telethon.tl.functions.bots import GetBotCommandsRequest, GetBotMenuButtonRequest
from telethon.tl.types import BotCommandScopePeerUser, InputPeerUser, BotMenuButtonCommands

# Get commands via TL request
scope = BotCommandScopePeerUser(peer=InputPeerUser(user_id=...), user_id=...)
commands = await demo_server.client(GetBotCommandsRequest(scope=scope, lang_code=""))
command_list = [BotCommandInfo(command=cmd.command, description=cmd.description) for cmd in commands]

# Get menu button via TL request
menu_button = await demo_server.client(GetBotMenuButtonRequest(user_id=InputPeerUser(user_id=...)))
menu_type = "commands" if isinstance(menu_button, BotMenuButtonCommands) else "default"
```

Note: The user_id is not directly available on the demo_server. The `_scope_key_from_telethon` function in `serverless_telethon_rpc.py` extracts user_id from `BotCommandScopePeer`. For the demo UI, using `BotCommandScopePeerUser` with a sentinel user_id (matching `client.user_id`) is the correct approach. However, since `DemoClientProtocol` doesn't expose `user_id`, the route should use `InputPeerUser(user_id=0, access_hash=0)` and the RPC handler should map `BotCommandScopePeerUser` to the client's chat scope. Alternatively, expose `chat_id` on the DemoServer or use `BotCommandScopeDefault`. Check the RPC handler's `_scope_key_from_telethon` to determine the right approach.

## Acceptance Criteria

1. `make check` passes.
2. No public `get_bot_state` method exists.
3. `/api/state` route uses Telethon TL requests.
4. `BotStateResponse` structure is unchanged (API contract preserved).
5. No file exceeds 200 lines.

## Risks

- **`routes.py` line count**: Adding TL request imports and construction logic adds lines. Currently 184 lines; may need to extract the state route into a helper module if it exceeds 200 lines.
- **Scope mapping complexity**: The RPC handler's `_scope_key_from_telethon` currently handles `BotCommandScopePeer` and `BotCommandScopeDefault`. May need to add `BotCommandScopePeerUser` handling. Check and extend if needed.
- **Menu button type detection**: The TL response is a `BotMenuButtonCommands` or `BotMenuButtonDefault` object. Ensure the isinstance check matches correctly.
