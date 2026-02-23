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
- **Not a Telethon replacement** — this is specifically for testing PTB bots
- **Not for real Telegram network tests** — all communication is simulated in-memory

## Core idea

You provide a `build_application` callback that configures your PTB `Application` with handlers. The library provides a `ServerlessTelegramClient` that mimics Telethon's client interface, bridging outgoing Bot API calls into Telethon TL objects for assertions.

## Quickstart

```python
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
from tg_auto_test.test_utils.serverless_telegram_client import ServerlessTelegramClient

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

## Public API (v0.1)

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

### ServerlessTelegramConversation

Async context manager for message exchange:

- `await conv.send_message(text: str)` — send text message
- `await conv.send_file(file: Path | bytes, *, caption: str = "", force_document: bool = False, voice_note: bool = False, video_note: bool = False)` — send file
- `await conv.get_response() -> ServerlessMessage` — get bot's response
- `await conv.click_inline_button(message_id: int, callback_data: str) -> ServerlessMessage` — click inline button

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
- `.reply_markup_data: dict | None` — raw reply markup data
- `await .download_media(file=bytes) -> bytes | None` — download media bytes
- `await .click(data: bytes) -> ServerlessMessage` — click inline button

### Supported Telethon RPC subset

- `GetBotCommandsRequest` — retrieve bot commands
- `GetBotMenuButtonRequest` — retrieve chat menu button
- `GetStarsStatusRequest` — get Stars balance
- `GetPaymentFormRequest` — get payment form for Stars invoice
- `SendStarsFormRequest` — submit Stars payment

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
- PTB-only bridge in v0.1 (architecture allows adding aiogram, raw HTTP adapters)
- Unsupported Bot API methods raise `AssertionError` (fail-fast design)
- No multi-user/multi-chat support yet (single private chat simulation)
- No message edit tracking, reactions, albums, polls
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