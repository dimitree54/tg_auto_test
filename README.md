# tg-auto-test

A serverless testing library for python-telegram-bot applications. Runs a real PTB `Application` in-process with a fake Bot API transport. Tests use Telethon-like interfaces for assertions.

## What it is

`tg-auto-test` allows you to write fast, reliable tests for your Telegram bots without making network calls to the real Telegram Bot API. It:

- Runs your python-telegram-bot `Application` in-process with all handlers intact
- Provides a fake Bot API transport that captures and responds to API calls
- Offers a `ServerlessTelegramClient` that mimics Telethon's client interface
- Bridges outgoing Bot API calls into Telethon TL objects for consistent test assertions
- Supports media files, inline keyboards, payments (Stars), and bot commands

## What it is NOT

- **Not a Telegram bot framework** — use python-telegram-bot for that
- **Not a Telethon replacement** — it is a fake Telethon, specifically for testing PTB bots
- **Not for real Telegram network tests** — all communication is simulated in-memory

## Design philosophy

`tg-auto-test` is a **fake Telethon**. The core idea is to build a drop-in replacement for Telethon's `TelegramClient` that works entirely in-memory — no internet connection, no Telegram account, no API tokens, no authentication.

Any code that accepts a Telethon client should also accept our `ServerlessTelegramClient` and get the same behavior. This includes the Demo UI bundled with this library: it works identically whether you pass a real `TelegramClient` or our fake one.

**Key principles:**

1. **We re-implement, not invent.** Our fake classes (`ServerlessTelegramClient`, `ServerlessMessage`, `ServerlessTelegramConversation`, `ServerlessButton`) mirror real Telethon public interfaces exactly — same method names, parameter names, positional/keyword-only markers, defaults, and types. We do not add custom public methods.

2. **Conformance tests enforce parity.** Forward conformance tests verify our fakes have no extra public methods beyond Telethon. Reverse conformance tests verify every Telethon public method exists on our fakes. Signature conformance tests verify parameter-level match using `inspect.signature()`. See `tests/unit/test_telethon_conformance_*.py` and `tests/unit/test_telethon_reverse_conformance_*.py`.

3. **Unimplemented methods fail loudly.** Any Telethon public method we haven't implemented raises `NotImplementedError` — never a silent no-op, never an `AttributeError`.

4. **`_`-prefixed internals are the exception.** Internal test infrastructure methods (like `_pop_response`, `_api_calls`) are prefixed with `_` and are not part of the Telethon interface contract.

5. **Single chat only.** The library simulates one private chat between a user and a bot. No multi-user, no group chats, no channels. This is a deliberate scope constraint.

## How it works

You provide a `build_application` callback that configures your PTB `Application` with handlers. The library provides a `ServerlessTelegramClient` that implements Telethon's client interface, bridging outgoing Bot API calls into Telethon TL objects for assertions.

## Quickstart

```python
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient, TelegramApiCall

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)

def build_app(builder: ApplicationBuilder) -> Application:
    app = builder.build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    return app

# In your test:
client = ServerlessTelegramClient(build_application=build_app)
await client.connect()
async with client.conversation("test_bot") as conv:
    await conv.send_message("hello")
    msg = await conv.get_response()
    assert msg.text == "hello"
await client.disconnect()
```

## Public API

### ServerlessTelegramClient

Main entry point for serverless testing:

```python
ServerlessTelegramClient(
    build_application: Callable[[ApplicationBuilder], Application],
    user_id: int = 9001,
    first_name: str = "Alice",
    bot_username: str = "test_bot",
    bot_first_name: str = "TestBot"
)
```

**Conversation management:**
- `conversation(entity, *, timeout=60.0)` — create conversation context manager

### ServerlessTelegramConversation

Async context manager for message exchange:

- `await conv.send_message(text: str)` — send text message
- `await conv.send_file(file: Path | bytes, *, caption: str = "", force_document: bool = False, voice_note: bool = False, video_note: bool = False)` — send file
- `await conv.get_response() -> ServerlessMessage` — get bot's response

### ServerlessMessage

Response object with Telethon-compatible interface:

- `.text: str` — message text
- `.photo: Photo | None` — photo media
- `.document: Document | None` — document media (excludes voice/video notes)
- `.voice: Document | None` — voice note media
- `.video_note: Document | None` — video note media
- `.file: TelethonFile | None` — Telethon File wrapper with `.size`, `.width`, `.height`, `.mime_type`, `.name`
- `.invoice: MessageMediaInvoice | None` — invoice details
- `.buttons: list[list[ServerlessButton]] | None` — keyboard button rows
- `.button_count: int` — total number of buttons
- `await .download_media(file=bytes) -> bytes | None` — download media bytes
- `await .click(data: bytes) -> ServerlessMessage` — click inline button

### TelegramApiCall

Data class representing a single Bot API call:

- `.api_method: str` — the API method name (e.g., "sendMessage", "getMe")
- `.parameters: dict[str, str]` — request parameters sent to the API
- `.file: FileData | None` — uploaded file data, if any
- `.result: JsonValue | None` — the API response result, if successful

### Supported Telethon RPC subset

- `GetBotCommandsRequest` — retrieve bot commands
- `GetBotMenuButtonRequest` — retrieve chat menu button
- `GetStarsStatusRequest` — get Stars balance
- `GetPaymentFormRequest` — get payment form for Stars invoice
- `SendStarsFormRequest` — submit Stars payment
- `SendVoteRequest` — vote in a poll

## Supported Bot API methods

Core messaging:
- `sendMessage` — send text messages with reply markup
- `editMessageText` — edit message text

Media:
- `sendDocument` — send documents
- `sendVoice` — send voice notes
- `sendPhoto` — send photos
- `sendVideoNote` — send video notes

Payments:
- `sendInvoice` — send Stars payment requests
- `answerPreCheckoutQuery` — approve/reject payment

Polls:
- `sendPoll` — send polls with multiple options

Interactive:
- `answerCallbackQuery` — respond to inline button presses

Bot configuration:
- `setMyCommands`, `getMyCommands`, `deleteMyCommands` — manage bot commands
- `setChatMenuButton`, `getChatMenuButton` — manage chat menu button

Utilities:
- `getMe` — get bot information
- `getFile` — get file information

## Limitations & extension seams

**Current limitations:**
- PTB-only bridge (architecture allows adding aiogram, raw HTTP adapters)
- Unsupported Bot API methods raise `AssertionError` (fail-fast design)
- Single private chat only — no multi-user, group chats, or channels
- No message edit tracking, reactions, or albums
- No support for `sendVideo`, `sendAudio`, `sendAnimation`, `sendLocation`, `sendSticker`

**Extension points:**
The architecture is designed to support additional frameworks and features. See `TODO.md` for planned extensions.

## Dependencies & licenses

**Runtime dependencies:**
- `python-telegram-bot` (LGPL-3.0) — **Users should be aware of LGPL implications for their projects**
- `Telethon` (MIT)
- `Pillow` (HPND, permissive)

**Development dependencies:**
- `pytest`, `pytest-asyncio`, `pytest-xdist` — testing
- `ruff`, `pylint`, `vulture` — code quality
- `build`, `twine` — packaging

## Contributing

**Prerequisites:**
- Python 3.12+
- `uv` package manager
- Node.js (for jscpd duplicate detection)

**Setup:**
```bash
uv sync --dev
```

**Quality gates:**
All Python execution must go through `uv`. Run `make check` before submitting PRs — it must pass 100%.

**Code style:**
- Enforced by ruff configuration
- 200-line module limit (enforced by linter)
- No `.env` files — this project uses Doppler for secrets management

See `CONTRIBUTING.md` for detailed guidelines.

## Demo UI

`tg-auto-test` includes a local web UI for interactive bot testing. The Demo UI accepts any Telethon-compatible client — both the real `TelegramClient` and our `ServerlessTelegramClient` work through the same standard Telethon interfaces. This is a practical proof that our fake client is a true drop-in replacement.

### What it is

The Demo UI is a local web server that provides:
- Browser-based chat interface for testing bots
- Support for text messages, media files (photos, documents, voice notes, video notes)
- Inline keyboard interaction (button clicking)
- Poll voting
- Stars payment simulation
- Bot state inspection (commands, menu buttons)

### Security

**⚠️ SECURITY WARNING:** The Demo UI is intended for localhost development only. Never expose it to public networks or production environments. It runs without authentication and could expose sensitive bot functionality.

### Installation

Install with the demo extra to get FastAPI and web server dependencies:

```bash
pip install tg-auto-test[demo]
```

### Quickstart: Serverless Mode

Use with `ServerlessTelegramClient` for fast, in-memory bot testing:

```python
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient
from tg_auto_test.demo_ui.server.demo_server import create_demo_app
import uvicorn

def build_app(builder):
    # Your PTB Application setup here
    app = builder.build()
    # Add handlers...
    return app

# Create serverless client
client = ServerlessTelegramClient(build_application=build_app)

# Create demo app
demo_app = create_demo_app(client=client, peer="test_bot")

# Run server
uvicorn.run(demo_app, host="127.0.0.1", port=8000)
```

Navigate to http://127.0.0.1:8000 to interact with your bot.

### Quickstart: Telethon Mode

Use with a real Telethon client for testing with authenticated sessions:

```python
from telethon import TelegramClient
from tg_auto_test.demo_ui.server.demo_server import create_demo_app
import uvicorn

# Create authenticated Telethon client
client = TelegramClient('session_name', api_id, api_hash)

# Create demo app
demo_app = create_demo_app(client=client, peer="@your_bot_username")

# Run server (client lifecycle managed automatically)
uvicorn.run(demo_app, host="127.0.0.1", port=8000)
```

### Supported features

- Text messages
- Media files (photos, documents, voice notes, video notes)
- Inline keyboards (button clicking and callback handling)
- Polls (creation and voting)
- Stars payments (invoice creation and payment simulation)
- Bot commands and menu button inspection

**Not yet supported:** message edit tracking, multi-chat, albums.