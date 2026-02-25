---
Sprint ID: `2026-02-25_complete-telethon-stubs`
Sprint Goal: `Add all 15 missing Telethon interface stubs/implementations to pass conformance tests; fix 4 Demo UI Telethon-compatibility bugs`
Status: `planning`
---

## Goal

Implement the 15 missing Telethon interface items (currently xfail) across `ServerlessTelegramClientCore`, `ServerlessMessage`, and `ServerlessTelegramConversation`. Every conformance test must pass (xfail markers removed). Fix 4 Demo UI routes that use private methods or assumptions that break with a real Telethon client.

## Scope

### In
- 4 client methods: `send_message`, `send_file`, `download_media`, `get_entity`
- 5 message methods: `delete`, `edit`, `reply`, `forward_to`, `get_reply_message`
- 19 message properties: `sender_id`, `chat_id`, `raw_text`, `reply_to_msg_id`, `sender`, `chat`, `forward`, `via_bot`, `sticker`, `contact`, `venue`, `audio`, `video`, `gif`, `game`, `web_preview`, `dice` (plus existing `voice`, `video_note`)
- 5 conversation methods: `cancel`, `cancel_all`, `wait_event`, `wait_read`, `mark_read`
- File decomposition of `serverless_telegram_client_core.py` (200 lines, at limit) and `serverless_message.py` (197 lines, near limit)
- Remove all 15 `xfail` markers from conformance tests
- Fix 4 Demo UI Telethon-compatibility bugs in `routes.py`:
  - Replace `_pop_response()` calls in `/api/invoice/pay` and `/api/poll/vote` with conversation pattern
  - Fix `/api/callback` to handle `msg.click()` returning `BotCallbackAnswer` (not Message)
  - Replace dummy `InputPeerUser(user_id=0)` / `InputPeerEmpty()` with `demo_server.peer` / `get_input_entity`
- Decompose `routes.py` (at 200-line limit) to accommodate fixes
- Update `DemoClientProtocol` to remove `_pop_response` dependency
- Update Demo UI test (`test_demo_server.py`) to remove `_pop_response` pattern

### Out
- Full event system implementation (wait_event raises NotImplementedError)
- Read receipts (wait_read, mark_read raise NotImplementedError)
- Multi-chat forwarding (forward_to raises NotImplementedError)
- Entity resolution (get_entity, sender, chat properties raise NotImplementedError)
- Frontend JS/CSS changes (no new visual elements needed for this sprint)

## Inputs (contracts)

- Requirements: User's original requirement "Add missing public telethon interfaces that exist in telethon but not in our lib"
- Architecture: Single-bot-chat constraint; methods within scope get real implementation, methods outside scope raise `NotImplementedError`
- Related: Previous sprint `docs/sprints/2026-02-24_telethon-interface-alignment/`

## Change digest

- **Requirement deltas**: Previous sprint left 15 conformance tests as xfail. This sprint resolves all 15. Additionally, 4 Demo UI routes use private methods (`_pop_response`) and dummy peer values that crash with real Telethon — these must be fixed to use standard Telethon patterns.
- **Architecture deltas**: `routes.py` decomposition needed (currently at 200-line limit, fixes will add lines). `DemoClientProtocol` updated (remove `_pop_response` assumption).

## Task list (dependency-aware)

- **T1:** `TASK_01_decompose_client_core.md` (depends: —) — Extract client public-API methods into a new `serverless_client_public_api.py` mixin, freeing space in `serverless_telegram_client_core.py`
- **T2:** `TASK_02_client_stubs.md` (depends: T1) — Add `send_message`, `send_file`, `download_media`, `get_entity` to the new mixin; remove 4 xfail markers
- **T3:** `TASK_03_decompose_message.md` (depends: —) (parallel: yes, with T1) — Extract message properties into a new `serverless_message_properties.py` mixin, freeing space in `serverless_message.py`
- **T4:** `TASK_04_message_properties.md` (depends: T3) — Add the 19 required properties (17 new + verify 2 existing); remove 1 xfail marker (test_message_additional_properties)
- **T5:** `TASK_05_message_methods.md` (depends: T3, T2) — Add `delete`, `edit`, `reply`, `forward_to`, `get_reply_message` to `ServerlessMessage`; remove 5 xfail markers
- **T6:** `TASK_06_conversation_stubs.md` (depends: —) (parallel: yes, with T1–T5) — Add `cancel`, `cancel_all`, `wait_event`, `wait_read`, `mark_read` to `ServerlessTelegramConversation`; remove 5 xfail markers
- **T7:** `TASK_07_demo_ui_compat.md` (depends: T2) — Fix 4 Demo UI Telethon-compatibility bugs: replace `_pop_response()` with conversation pattern, fix `click()` return type handling, replace dummy peers; decompose `routes.py` to stay under 200 lines; update `DemoClientProtocol`; update `test_demo_server.py`
- **T8:** `TASK_08_vulture_whitelist.md` (depends: T2, T4, T5, T6, T7) — Update `vulture_whitelist.py` for all new public symbols; final `make check` validation

## Dependency graph (DAG)

- T1 → T2
- T3 → T4
- T3 → T5
- T2 → T5 (message.reply delegates to client.send_message)
- T1 → T5 (message methods need client reference understanding)
- T2 → T7 (Demo UI fix uses conversation pattern which needs send_message on client)
- T2 → T8
- T4 → T8
- T5 → T8
- T6 → T8
- T7 → T8

## Execution plan

### Critical path
T1 → T2 → T7 → T8

### Parallel tracks (lanes)

- **Lane A (Client)**: T1 → T2
- **Lane B (Message)**: T3 → T4 → T5 (T5 waits for T2 as well)
- **Lane C (Conversation)**: T6 (fully independent)
- **Lane D (Demo UI)**: T7 (waits for T2; parallel with T4, T5, T6)
- **Lane E (Finalize)**: T8 (waits for T2, T4, T5, T6, T7)

## Production safety

This is a **testing library** — there is no production database and no deployed service. All changes are to Python source code and tests.

- **Production database**: N/A — no database in this project
- **Shared resource isolation**: N/A — library code only
- **Migration deliverable**: N/A — no data model changes

## Definition of Done (DoD)

All items must be true:

- All 15 xfail markers removed from conformance tests
- All 15 previously-xfail tests pass
- Demo UI routes contain zero private-method calls (`_pop_response`, `_outbox`, etc.)
- Demo UI routes use no dummy peer values (`InputPeerEmpty()`, `InputPeerUser(user_id=0)`)
- `make check` is 100% green (ruff format, ruff check, pylint 200-line limit, vulture, jscpd, pytest)
- No file exceeds 200 lines
- Zero legacy tolerance: no dead code, no duplicate `_wrap_button_row`, no orphaned imports
- No errors are silenced (no swallowed exceptions; no "pretend success")
- Requirements/architecture docs unchanged

## Risks + mitigations

- **Risk**: Telethon `Message.delete/edit/reply/forward_to` use `*args, **kwargs` signatures — our conformance tests compare parameter names, so our stub must match exactly.
  - **Mitigation**: Verified: test checks `list(telethon_params.keys()) == list(our_params.keys())`. Telethon params are `{'args': VAR_POSITIONAL, 'kwargs': VAR_KEYWORD}`. Our stubs must use identical `*args, **kwargs` signatures.

- **Risk**: `serverless_message.py` decomposition may break imports throughout codebase.
  - **Mitigation**: Use a mixin/base-class pattern. `ServerlessMessage` keeps its import path via `models.py` re-export. Existing code doesn't change import paths.

- **Risk**: Adding properties to a `@dataclass(slots=True)` class is tricky — properties don't work with slots unless declared as `__slots__` fields.
  - **Mitigation**: Existing code already uses `@property` on `ServerlessMessage` (a slots dataclass) — this works because properties are defined on the class, not as instance attributes. New properties follow the same pattern.

- **Risk**: Circular import between `ServerlessMessage` and `ServerlessTelegramClientCore` when `message.reply()` needs to call `client._process_text_message()`.
  - **Mitigation**: `ServerlessMessage` already has `_click_callback` pattern — add a similar `_client` reference callback for reply/edit/delete operations.

- **Risk**: `routes.py` is at exactly 200 lines. Fixing the 4 bugs (replacing `_pop_response` with conversation pattern, fixing callback handling) will add lines.
  - **Mitigation**: Extract invoice/poll/callback route handlers into a new `routes_interactive.py` file (following `upload_handlers.py` pattern).

- **Risk**: `test_demo_server.py` test `test_poll_vote_endpoint` uses a `MockClient` with `_pop_response()` — this test validates the current broken behavior and must be updated.
  - **Mitigation**: Update mock to use conversation pattern, matching the fixed route implementation.

- **Risk**: Real Telethon `msg.click()` returns `BotCallbackAnswer` not `Message`. The callback route passes the result to `serialize_message()` which expects Message properties.
  - **Mitigation**: Change callback route to use conversation pattern (send callback query via conversation, get response via `conv.get_response()`) instead of relying on `click()` return value.

## Migration plan (if data model changes)

N/A — no data model changes.

## Rollback / recovery notes

- Revert the commits for this sprint. All changes are additive (new methods/properties) with no behavior changes to existing methods.

## Task validation status

- T1: self-validated (A-F pass: pure refactoring, no dependencies, parallel-safe, testable ACs)
- T2: self-validated (A-F pass: signatures verified at runtime, dependency on T1 explicit, line count risk addressed)
- T3: self-validated (A-F pass: pure refactoring, parallel with T1/T6, slots+mixin pattern verified)
- T4: self-validated (A-F pass: properties verified via hasattr, dependency on T3, line count OK)
- T5: self-validated (A-F pass: *args/**kwargs signature verified, depends on T3+T2, NotImplementedError justified)
- T6: self-validated (A-F pass: fully independent, sync/async correctness verified against Telethon source)
- T7: self-validated (A-F pass: 4 concrete bugs, decomposition strategy clear, test updates included)
- T8: self-validated (A-F pass: final gate task, depends on all, whitelist-only changes)

## Sources used

- Requirements: User's sprint planning prompt
- Architecture: Single-bot-chat constraint (from user's prompt)
- Code read (for scoping only):
  - `tg_auto_test/test_utils/serverless_telegram_client_core.py` (200 lines)
  - `tg_auto_test/test_utils/serverless_message.py` (197 lines)
  - `tg_auto_test/test_utils/serverless_telegram_conversation.py` (72 lines)
  - `tg_auto_test/test_utils/serverless_message_helpers.py` (33 lines)
  - `tg_auto_test/test_utils/serverless_client_helpers.py` (48 lines)
  - `tg_auto_test/test_utils/models.py` (38 lines)
  - `tg_auto_test/test_utils/message_factory.py` (174 lines)
  - `tg_auto_test/test_utils/response_processor.py` (56 lines)
  - `tg_auto_test/test_utils/serverless_update_processor.py` (40 lines)
  - `tg_auto_test/test_utils/serverless_telegram_client.py` (39 lines)
  - `tg_auto_test/demo_ui/server/routes.py` (200 lines)
  - `tg_auto_test/demo_ui/server/serialize.py` (173 lines)
  - `tg_auto_test/demo_ui/server/demo_server.py` (142 lines)
  - `tg_auto_test/demo_ui/server/api_models.py` (47 lines)
  - `tg_auto_test/demo_ui/server/upload_handlers.py` (57 lines)
  - `tests/unit/test_telethon_conformance_client_extended.py` (85 lines)
  - `tests/unit/test_telethon_conformance_message_extended.py` (125 lines)
  - `tests/unit/test_telethon_conformance_conversation.py` (138 lines)
  - `tg_auto_test/test_utils/serverless_telethon_rpc.py` (130 lines)
  - `tg_auto_test/test_utils/file_processing_utils.py` (129 lines)
  - `tg_auto_test/test_utils/serverless_telegram_client.py` (39 lines)
  - `tests/unit/test_demo_server.py` (175 lines)
  - `tests/unit/test_demo_server_api_state.py` (129 lines)
  - `vulture_whitelist.py` (49 lines)
  - `Makefile` (15 lines)

## Contract summary

### What (requirements)
- Add all missing Telethon public interfaces to our fake testing library
- Methods within single-bot-chat scope: implement
- Methods outside scope: raise NotImplementedError
- All 15 xfail conformance tests must pass

### How (architecture)
- File decomposition via mixin pattern to stay under 200-line limit
- New files: `serverless_client_public_api.py` (client mixin), `serverless_message_properties.py` (message mixin), `routes_interactive.py` (Demo UI route extraction)
- `*args, **kwargs` signature matching for Message methods (Telethon uses this pattern)
- `_client` back-reference on ServerlessMessage for reply/edit/delete delegation
- Demo UI routes rewritten to use conversation pattern instead of `_pop_response()` and to handle `click()` return type correctly

## Impact inventory (implementation-facing)

- **Flows**: Client send_message/send_file/download_media become public API; message edit/delete/reply usable in tests; Demo UI invoice/poll/callback routes use Telethon-standard patterns
- **Modules / interfaces**: 2 new mixin files, 1 new route handler file, 4 modified source files, 4 modified test files, 1 modified whitelist, 1 modified protocol
- **Data model / migrations**: None
- **Security / privacy**: None
- **Performance / quality**: No performance impact; all new methods are thin wrappers or raise NotImplementedError

## Decisions (made from docs; not invented)

- D1: Message.delete/edit/reply/forward_to must use `*args, **kwargs` to match Telethon's exact signature (Source: `inspect.signature()` output confirming Telethon uses `*args, **kwargs`)
- D2: Properties that require entity resolution (`sender`, `chat`, `forward`, `via_bot`) raise NotImplementedError (Source: user's guidance — "outside single-bot-chat scope")
- D3: Conversation `cancel`/`cancel_all` implemented (set cancelled flag); `wait_event`/`wait_read`/`mark_read` raise NotImplementedError (Source: user's guidance + Telethon docs — event system and read receipts are out of scope)
- D4: Demo UI has 4 Telethon-compatibility bugs that must be fixed: `_pop_response()` usage (lines 133, 191), `click()` return type (line 149), dummy peer values (lines 66, 129, 182). Fix uses conversation pattern for invoice/poll/callback. (Source: user-confirmed analysis of `routes.py`)

## Non-goals

- NG1: Full event system implementation (Source: user's guidance — "event system is out of scope")
- NG2: Frontend visual changes for edit/delete indicators (Source: sprint scope — no UI requirement in the user's prompt beyond "consider if needed"; analysis shows it's not needed for conformance)
- NG3: Making Demo UI work with a live Telegram server (Source: this library is for testing, not production Telegram access — but routes should use standard Telethon patterns so they are portable)
