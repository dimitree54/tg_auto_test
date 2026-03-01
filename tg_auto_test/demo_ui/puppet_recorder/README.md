# Puppet Recorder (Experimental)

Record your manual bot interactions in a browser and export them as ready-to-run pytest tests.

The Puppet Recorder is a separate demo server that wraps the same `DemoClientProtocol` you already use with the Demo UI. Every message, file upload, button click, payment, and poll vote you perform in the browser is captured. When you're done, click **Export** to get a complete pytest function that replays the session using `ServerlessTelegramClient`.

## Quickstart

Replace `create_demo_app` with `create_puppet_recorder_app` — the signature is the same:

### Serverless mode

```python
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient
from tg_auto_test.demo_ui.puppet_recorder.recorder_server import create_puppet_recorder_app
import uvicorn

client = ServerlessTelegramClient(build_application=build_app)
app = create_puppet_recorder_app(client=client, peer="test_bot")
uvicorn.run(app, host="127.0.0.1", port=8000)
```

### Telethon mode

```python
from telethon import TelegramClient
from tg_auto_test.demo_ui.puppet_recorder.recorder_server import create_puppet_recorder_app
import uvicorn

client = TelegramClient("session_name", api_id, api_hash)
app = create_puppet_recorder_app(client=client, peer="@your_bot_username")
uvicorn.run(app, host="127.0.0.1", port=8000)
```

Open http://127.0.0.1:8000 — you will see a chat panel on the left and a recorder panel on the right.

## Recording a test

1. **Start recording** — click the **Record** button in the recorder panel (top-right). The status indicator turns red.
2. **Interact with your bot** — send messages, upload files, click inline buttons, pay invoices, vote in polls. Everything works exactly like the regular Demo UI.
3. **Stop recording** — click **Stop** when you are done. Steps recorded so far are preserved.
4. **Review** — switch between the **Steps** tab (list of captured actions) and the **Code** tab (live pytest preview).
5. **Export** — click **Export** to download the generated test as a `.py` file.
6. **Clear** — click **Clear** to discard recorded steps and start over.

Recording is independent of the chat: you can stop recording, keep chatting, and start again — only interactions performed while recording is active are captured.

## What gets recorded

| Action | Recorded fields |
|--------|----------------|
| Text message | message text, bot response text |
| Photo upload | file type, caption, bot response |
| Document upload | file type, bot response |
| Voice note | file type, bot response |
| Video note | file type, bot response |
| Inline button click | callback_data, message id, bot response |
| Invoice payment | message id, bot response |
| Poll vote | message id, selected option ids, bot response |

## Generated test output

The exported code is a standalone pytest function. Example:

```python
import pytest

from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient


@pytest.mark.asyncio
async def test_recorded_session(build_application) -> None:
    """Auto-generated test from puppet recorder session."""
    client = ServerlessTelegramClient(build_application=build_application)
    await client.connect()
    try:
        async with client.conversation("test_bot") as conv:
            peer = "test_bot"
            await conv.send_message("/start")
            response = await conv.get_response()
            assert response.text == "Welcome!"

            await conv.send_message("hello")
            response = await conv.get_response()
            assert response.text == "Echo: hello"
    finally:
        await client.disconnect()
```

The generated code expects a `build_application` pytest fixture that returns your PTB `Application`. Provide it in your `conftest.py`, just like you would for any other serverless test.

## API reference

All endpoints are under `/api/`. The chat endpoints (`/api/message`, `/api/photo`, etc.) behave the same as the regular Demo UI — the recorder hooks into them transparently.

### Recording control

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/recording/start` | Start recording interactions |
| POST | `/api/recording/stop` | Stop recording (preserves steps) |
| POST | `/api/recording/clear` | Discard all recorded steps |
| GET | `/api/recording/status` | Returns `{"recording": bool, "step_count": int}` |
| GET | `/api/recording/steps` | Returns the list of recorded steps as JSON |
| GET | `/api/recording/export` | Returns generated pytest code as `text/x-python` |

## Differences from the regular Demo UI

The Puppet Recorder is a **separate** server — it does not modify or replace the existing Demo UI in any way. Key differences:

- Self-contained HTML template (no Vite/TypeScript build step required)
- Adds the recorder panel alongside the chat
- Every chat route records a `RecordedStep` when recording is active
- Adds `/api/recording/*` control endpoints
- No bot state inspection (commands, menu buttons) — focused on interaction recording
