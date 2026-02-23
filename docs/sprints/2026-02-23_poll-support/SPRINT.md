# Sprint: Poll Support End-to-End

**Date:** 2026-02-23
**Goal:** Add poll support across `proto_tg_bot` (consumer) and `tg-auto-test` (library), covering bot command, serverless testing infrastructure, and demo UI.

## Task Order and Dependencies

```
TASK_01  (proto_tg_bot: /poll command + tests)
   │
   ▼
TASK_02  (tg-auto-test: sendPoll in StubTelegramRequest + message factory + models)
   │
   ▼
TASK_03  (tg-auto-test: process_poll_answer on ServerlessTelegramClientCore)
   │
   ▼
TASK_04  (tg-auto-test: demo UI poll rendering + vote endpoint)
   │
   ▼
TASK_05  (publish tg-auto-test 0.5.0, update proto_tg_bot, verify green)
```

TASK_01 has no dependencies — it intentionally writes tests that fail until the library catches up.

TASK_02 and TASK_03 are both in tg-auto-test but TASK_03 depends on TASK_02 (it needs the poll tracking data structures that TASK_02 introduces).

TASK_04 depends on TASK_02 + TASK_03 (the demo UI needs poll data on `ServerlessMessage` and `process_poll_answer` on the client).

TASK_05 depends on all previous tasks.

## Repos

| Repo | Path | Current version |
|------|------|-----------------|
| `tg-auto-test` | `/Users/yid/source/tg_auto_test` | 0.4.0 |
| `proto_tg_bot` | `/Users/yid/source/proto_tg_bot` | 0.1.0 (depends on `tg-auto-test==0.4.0`) |

## Key Constraints

- Both repos enforce a 200-line file limit — decompose rather than compact.
- Both repos use strict linting (`make check` must be 100% green).
- `ServerlessMessage` must expose poll data via Telethon-compatible types (`MessageMediaPoll`) so assertions work identically on serverless and serverfull backends.
- `process_poll_answer` must construct a PTB `PollAnswer` update and route it through the application's handler dispatch, matching how Telegram delivers poll answer updates.

## Tasks

| ID | Title | Repo | Depends on |
|----|-------|------|------------|
| TASK_01 | Add /poll command and PollAnswerHandler to proto_tg_bot | proto_tg_bot | — |
| TASK_02 | Add sendPoll to StubTelegramRequest + message factory + models | tg-auto-test | — |
| TASK_03 | Add process_poll_answer to ServerlessTelegramClientCore | tg-auto-test | TASK_02 |
| TASK_04 | Add poll support to demo UI | tg-auto-test | TASK_02, TASK_03 |
| TASK_05 | Publish 0.5.0 and update proto_tg_bot | both | TASK_01–04 |
