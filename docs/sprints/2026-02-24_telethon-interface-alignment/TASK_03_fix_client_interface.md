---
Task ID: `T3`
Title: `Fix ServerlessTelegramClient public interface`
Depends on: `T2`
Parallelizable: `no`
Owner: `Developer`
Status: `planned`
---

## Goal / value

`ServerlessTelegramClient` and `ServerlessTelegramClientCore` public methods match real Telethon 1.42 `TelegramClient` signatures exactly. All non-Telethon public attributes are privatized. Conformance tests for client methods pass (xfail markers removed).

## Context (contract mapping)

- Requirements: Divergences #1-6 from sprint request
- Telethon reference: [TelegramClient docs](https://docs.telethon.dev/en/stable/modules/client.html)

## Preconditions

- T2 complete (conformance tests exist and client-related ones are xfail)

## Non-goals

- Fixing message, button, or conversation interfaces (T4/T5)
- Implementing full Telethon behavior for newly added params (NotImplementedError is fine)
- Changing demo UI protocols (T6)

## Touched surface (expected files / modules)

- `tg_auto_test/test_utils/serverless_telegram_client_core.py` (primary)
- `tg_auto_test/test_utils/serverless_telegram_client.py` (primary)
- `tg_auto_test/test_utils/serverless_telegram_conversation.py` (update `ConversationClient` protocol)
- `tg_auto_test/test_utils/serverless_update_processor.py` (references `self.chat_id` etc.)
- `tg_auto_test/test_utils/serverless_stars_payment.py` (references `self._helpers`)
- `tg_auto_test/test_utils/serverless_telethon_rpc.py` (may reference client attributes)
- `tg_auto_test/test_utils/telethon_compatible_message.py` (references client)
- `tg_auto_test/demo_ui/server/demo_server.py` (DemoClientProtocol -- note: protocol FIX is T6, but attribute renames here may require interim updates)
- `tg_auto_test/demo_ui/server/routes.py` (references `demo_server.client._pop_response()`)
- `tg_auto_test/demo_ui/server/upload_handlers.py` (calls `client.conversation(peer, timeout)`)
- `tests/unit/test_serverless_client_text.py`
- `tests/unit/test_serverless_client_callbacks.py`
- `tests/unit/test_serverless_client_media.py`
- `tests/unit/test_serverless_client_api_calls.py`
- `tests/unit/test_serverless_client_reply_markup.py`
- `tests/unit/test_serverless_client_stars_payments.py`
- `tests/unit/test_serverless_client_poll.py`
- `tests/unit/test_serverless_poll_answer.py`
- `tests/unit/test_serverless_telethon_bot_commands_reset.py`
- `tests/unit/test_serverless_telethon_menu_button.py`
- `tests/unit/test_demo_server.py`
- `tests/unit/test_demo_server_api_state.py`
- `tests/unit/test_demo_integration.py`
- `tests/unit/test_telethon_conformance*.py` (remove xfail markers)
- `vulture_whitelist.py`

## Dependencies and sequencing notes

- Depends on T2 (conformance tests must exist first)
- Must complete before T6 (demo UI depends on aligned client)
- Serialized with T4/T5 due to shared files (models.py references, test files, vulture_whitelist)

## Third-party / library research (mandatory for any external dependency)

- **Library**: Telethon 1.42.x
  - **Conversation**: `conversation(entity, *, timeout=60.0, total_timeout=None, max_messages=100, exclusive=True, replies_are_responses=True)` -- [DialogMethods.conversation](https://docs.telethon.dev/en/stable/modules/client.html#telethon.client.dialogs.DialogMethods.conversation)
  - **get_messages**: `get_messages(entity, limit=None, *, offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, search=None, filter=None, from_user=None, wait_time=None, ids=None, reverse=False, reply_to=None, scheduled=False)` -- [MessageMethods.get_messages](https://docs.telethon.dev/en/stable/modules/client.html#telethon.client.messages.MessageMethods.get_messages)
  - **get_me**: `get_me(input_peer=False)` -- [UserMethods.get_me](https://docs.telethon.dev/en/stable/modules/client.html#telethon.client.users.UserMethods.get_me)
  - **get_input_entity**: `get_input_entity(peer)` -- [UserMethods.get_input_entity](https://docs.telethon.dev/en/stable/modules/client.html#telethon.client.users.UserMethods.get_input_entity)
  - **get_dialogs**: `get_dialogs(limit=None, *, offset_date=None, offset_id=0, offset_peer=..., ignore_pinned=False, ignore_migrated=False, folder=None)` -- [DialogMethods.get_dialogs](https://docs.telethon.dev/en/stable/modules/client.html#telethon.client.dialogs.DialogMethods.get_dialogs)

## Implementation steps (developer-facing)

### Step 1: Fix `conversation()` signature (Divergence #1)

In `serverless_telegram_client_core.py`:

**Before**: `def conversation(self, bot_username: str, timeout: int = 10)`
**After**: `def conversation(self, entity: object, *, timeout: float = 60.0, total_timeout: float | None = None, max_messages: int = 100, exclusive: bool = True, replies_are_responses: bool = True)`

- Rename `bot_username` to `entity`
- Make `timeout` keyword-only (add `*` before it)
- Change default from `10` to `60.0`, type from `int` to `float`
- Add remaining params; raise `NotImplementedError` if `total_timeout`, `max_messages`, `exclusive`, or `replies_are_responses` are passed with non-default values
- Delete the `del bot_username, timeout` line; just `del entity` (timeout may be used later)

### Step 2: Fix `get_messages()` signature (Divergence #2)

In `serverless_telegram_client_core.py`:

**Before**: `async def get_messages(self, entity: str, ids: int | list[int])`
**After**: `async def get_messages(self, entity: object, limit: int | None = None, *, offset_date: object = None, offset_id: int = 0, max_id: int = 0, min_id: int = 0, add_offset: int = 0, search: str | None = None, filter: object = None, from_user: object = None, wait_time: float | None = None, ids: int | list[int] | None = None, reverse: bool = False, reply_to: int | None = None, scheduled: bool = False)`

- Make `ids` keyword-only
- Add all other params from Telethon signature
- Raise `NotImplementedError` if any param besides `entity` and `ids` is passed with non-default value
- Raise `ValueError` if both `ids` is None and `limit` is None (Telethon requires one or the other)

**Note**: This changes the call sites. All callers currently pass `ids` positionally:
- `routes.py` line 144: `await demo_server.client.get_messages(demo_server.peer, ids=req.message_id)` -- already keyword! OK.
- `test_serverless_client_callbacks.py` line 74: `await client.get_messages("test_bot", ids=msg_with_buttons.id)` -- already keyword! OK.

### Step 3: Fix `get_me()` signature (Divergence #3)

In `serverless_telegram_client_core.py`:

**Before**: `async def get_me(self) -> User`
**After**: `async def get_me(self, input_peer: bool = False) -> User`

- Add `input_peer` param
- If `input_peer=True`, raise `NotImplementedError("input_peer=True not supported")`

### Step 4: Fix `get_dialogs()` signature (Divergence #4)

In `serverless_telegram_client_core.py`:

**Before**: `async def get_dialogs(self) -> list[str]`
**After**: `async def get_dialogs(self, limit: int | None = None, *, offset_date: object = None, offset_id: int = 0, offset_peer: object = None, ignore_pinned: bool = False, ignore_migrated: bool = False, folder: int | None = None) -> list[object]`

- Add all Telethon params
- Keep returning `[]` (empty list) as the stub behavior
- Return type `list[object]` to approximate `TotalList[Dialog]`

### Step 5: Fix `get_input_entity()` param name (Divergence #5)

In `serverless_telegram_client.py`:

**Before**: `async def get_input_entity(self, entity: str) -> InputPeerUser`
**After**: `async def get_input_entity(self, peer: object) -> InputPeerUser`

- Rename `entity` to `peer`
- Update `del entity` to `del peer`

### Step 6: Privatize public attributes (Divergence #6)

In `serverless_telegram_client_core.py` `__init__`:

**Before**:
```python
self.request = StubTelegramRequest(...)
self.application = build_application(builder)
self.chat_id, self.user_id, self.first_name = user_id, user_id, first_name
```

**After**:
```python
self._request = StubTelegramRequest(...)
builder = Application.builder().token(_FAKE_TOKEN).request(self._request)
self._application = build_application(builder)
self._chat_id, self._user_id, self._first_name = user_id, user_id, first_name
```

Then update ALL internal references:
- `self.request` -> `self._request` throughout `serverless_telegram_client_core.py`
- `self.application` -> `self._application` throughout
- `self.chat_id` -> `self._chat_id` throughout
- `self.user_id` -> `self._user_id` throughout
- `self.first_name` -> `self._first_name` throughout
- Also update references in `serverless_telegram_client.py`, `serverless_update_processor.py`, `serverless_stars_payment.py`, `serverless_telethon_rpc.py`, and any other file that accesses these attributes

### Step 7: Update `_api_calls` and `_last_api_call` to reference `_request`

These already use `self.request.calls` -- update to `self._request.calls`.

### Step 8: Update all test files

Search all test files for:
- `client.request` -> `client._request` (if any direct access; likely minimal since these are already `_api_calls`)
- `client.chat_id` -> `client._chat_id` (if any)
- `client.application` -> `client._application` (if any)
- `client.conversation("test_bot")` -- this still works since `entity` is positional

Add `# noqa: SLF001` where tests access private attributes for verification.

### Step 9: Update `vulture_whitelist.py`

Remove entries for symbols that were renamed or removed. Add new entries for renamed private symbols if vulture flags them.

### Step 10: Remove xfail markers from T2 conformance tests

For all client-related conformance tests (divergences #1-6), remove the `pytest.mark.xfail` markers.

### Step 11: Run `make check`

Verify everything passes: ruff, pylint (200-line check), vulture, jscpd, pytest.

## Production safety constraints (mandatory)

N/A -- library code changes; no database, no deployed service, no shared resources.

## Anti-disaster constraints (mandatory)

- **Reuse before build**: Renaming existing attributes, not adding new modules.
- **Correct file locations**: Changes in existing files at existing paths.
- **No regressions**: All 18+ existing tests must pass. Run `make check` after every step group.

## Error handling + correctness rules (mandatory)

- New params that aren't implemented raise `NotImplementedError("param_name not supported")` -- never silently ignored.
- `get_messages()` with neither `ids` nor `limit` raises `ValueError`.

## Zero legacy tolerance rule (mandatory)

- Old param names (`bot_username` in conversation, `entity` in get_input_entity) are completely removed -- no aliases, no backward compat.
- Old public attribute names (`request`, `application`, `chat_id`, `user_id`, `first_name`) are completely privatized -- no public wrappers kept for compatibility.

## Acceptance criteria (testable)

1. `conversation()` signature matches Telethon: `entity` param (positional), `timeout` keyword-only with default `60.0`, all additional params present.
2. `get_messages()` has `ids` as keyword-only, all Telethon params present.
3. `get_me(input_peer=False)` signature matches Telethon.
4. `get_dialogs()` has all Telethon params.
5. `get_input_entity(peer)` param named `peer`.
6. No public (non-underscore) instance attributes remain that aren't on Telethon's client.
7. All conformance tests for client methods pass (xfail markers removed).
8. All existing tests pass.
9. `make check` passes 100%.
10. All modified files <= 200 lines.

## Verification / quality gates

- [ ] `make check` passes
- [ ] Client conformance tests pass (no xfail)
- [ ] No public attribute `request`, `application`, `chat_id`, `user_id`, `first_name` on client
- [ ] All files <= 200 lines

## Edge cases

- `serverless_telegram_client_core.py` is 183 lines currently. Adding params to multiple methods may push it over 200. If so, extract helper methods or move some methods to a mixin file.
- Demo UI `routes.py` and `upload_handlers.py` call `client.conversation(peer, timeout)` with `timeout` as positional. After making `timeout` keyword-only, these calls must be updated to `client.conversation(peer, timeout=timeout)`.
- `routes.py` is exactly 200 lines. Any changes must not increase line count. The keyword argument change (`timeout=`) doesn't add lines.

## Notes / risks

- **Risk**: Renaming `self.request` to `self._request` may break internal files not listed above.
  - **Mitigation**: Use project-wide search for `self.request` and `.request.` to find all references before renaming.
- **Risk**: `serverless_telegram_client_core.py` exceeds 200 lines after adding params.
  - **Mitigation**: The `get_messages` and `get_dialogs` methods need many params. Consider extracting a `_check_unsupported_params()` helper to validate NotImplementedError params in fewer lines.
