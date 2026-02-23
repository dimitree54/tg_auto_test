# TASK_04 — Add poll support to demo UI

**Repo:** `/Users/yid/source/tg_auto_test`
**Dependencies:** TASK_02, TASK_03

## Description

Make polls render in the demo web UI and allow users to vote by clicking options. This spans the Python backend (serializer, routes, API models) and the TypeScript frontend.

### Backend changes

#### Serializer (`serialize.py`)

Update `serialize_message` to detect poll messages. When `message.poll` is not `None`, return a `MessageResponse` with:
- `type`: `"poll"`
- `poll_question`: the question string
- `poll_options`: list of `{"text": "...", "voter_count": 0}` dicts
- `poll_id`: the poll ID string
- `message_id`: the message ID

#### API models (`api_models.py`)

- Add `"poll"` to the `MessageResponse.type` comment/docs.
- Add optional fields to `MessageResponse`: `poll_question`, `poll_options`, `poll_id`.
- Add a `PollVoteRequest` model: `poll_id: str`, `option_ids: list[int]`.

#### Routes (`routes.py`)

Add a new endpoint:
```
POST /api/poll/vote
Body: {"poll_id": "poll_1", "option_ids": [0]}
```

This endpoint calls `demo_server.client.process_poll_answer(poll_id, option_ids)` and returns the serialized bot response.

The `DemoClientProtocol` in `demo_server.py` needs a `process_poll_answer` method added.

### Frontend changes

#### Types (`web/src/types/api.ts`)

- Add `"poll"` to the `MessageType` union.
- Add optional `poll_question`, `poll_options`, `poll_id` fields to `MessageResponse`.

#### API client (`web/src/api/bot.ts`)

Add a `votePoll(pollId: string, optionIds: number[])` function that POSTs to `/api/poll/vote`.

#### Message rendering (`web/src/ui/messages.ts`)

Add an `addPollMessage(data, type)` function that renders:
- The poll question as a heading.
- Each option as a clickable button.
- When a button is clicked, call `votePoll` and render the bot's text response.

Update `renderBotResponse` to handle `data.type === 'poll'`.

#### Send flow (`web/src/flows/send.ts`)

No changes needed — polls are triggered by text commands like `/poll` which already go through `sendTextMessage`.

## Files to modify/create

| File | Action |
|------|--------|
| `tg_auto_test/demo_ui/server/serialize.py` | Handle `message.poll` in `serialize_message` |
| `tg_auto_test/demo_ui/server/api_models.py` | Add `PollVoteRequest`, add poll fields to `MessageResponse` |
| `tg_auto_test/demo_ui/server/routes.py` | Add `POST /api/poll/vote` endpoint |
| `tg_auto_test/demo_ui/server/demo_server.py` | Add `process_poll_answer` to `DemoClientProtocol` |
| `web/src/types/api.ts` | Add `"poll"` type and poll fields |
| `web/src/api/bot.ts` | Add `votePoll` function |
| `web/src/ui/messages.ts` | Add `addPollMessage`, update `renderBotResponse` |
| `tests/unit/test_demo_serialize.py` | Add test for poll message serialization |
| `tests/unit/test_demo_server.py` | Add test for `/api/poll/vote` endpoint |

## Acceptance Criteria

1. When a bot sends a poll (via `/poll` command), the demo UI renders the question and clickable option buttons.
2. Clicking an option sends `POST /api/poll/vote` with the poll_id and selected option_id.
3. The backend calls `process_poll_answer` and returns the bot's response.
4. The bot's response text (e.g., "You voted for: Red") renders in the chat.
5. `serialize_message` correctly serializes `ServerlessMessage` with poll data to `MessageResponse`.
6. Unit tests cover poll serialization and the vote endpoint.
7. Frontend builds without errors (`npm run build` in `web/`).
8. `make check` is 100% green.

## Risks / Notes

- `routes.py` is at 195 lines — adding the poll vote endpoint will exceed 200. Extract the file-upload helpers or group poll routes into a separate module (e.g., `routes_poll.py`).
- `messages.ts` is at 290 lines — already well over 200. The poll rendering function should go in a new file (e.g., `web/src/ui/poll.ts`). The 200-line limit applies to Python files; check if the JS/TS linter has a similar constraint.
- The `DemoClientProtocol` must be updated to include `process_poll_answer` so that type checking passes.
- Poll rendering should support both single-answer and multiple-answer polls (checkboxes vs radio buttons in the UI), though for this sprint single-answer is sufficient.
