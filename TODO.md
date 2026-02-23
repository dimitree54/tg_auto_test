# TODO.md

Categorized backlog of planned features and improvements for tg-auto-test.

## Bot API coverage gaps

**Missing media methods:**
- `sendVideo` — send video files
- `sendAudio` — send audio files  
- `sendAnimation` — send GIFs/animations
- `sendLocation` — send location data
- `sendSticker` — send sticker files

**Missing message operations:**
- Message editing tracking — track when messages are edited
- Message deletion — `deleteMessage` method
- `forwardMessage` — forward messages between chats

**Missing interactive features:**
- Inline query support — `answerInlineQuery`
- Web app support — `answerWebAppQuery`

## Telethon parity gaps

**Entity parsing:**
- User/chat entity resolution beyond basic `InputPeerUser`
- Support for channel/group entities
- Entity caching for realistic behavior

**Message features:**
- Reactions — add/remove message reactions
- Albums — grouped media messages
- Polls — create and interact with polls
- Message threading — reply chains

**Advanced media:**
- Media groups/albums
- Live location updates
- Contact sharing

## Multi-user/multi-chat support

**Multi-user scenarios:**
- Simulate multiple users interacting with bot
- Group chat simulation with multiple participants
- Admin/user role simulation in groups

**Multi-chat support:**
- Private chats, group chats, channels
- Chat-specific settings and permissions
- Cross-chat message forwarding

## Framework adapters

**aiogram support:**
- Adapter for aiogram bots (similar to current PTB adapter)
- aiogram-specific handler patterns
- aiogram middleware testing

**Raw HTTP Bot API adapter:**
- Direct HTTP Bot API testing without framework dependencies
- Webhook simulation for serverless bots
- Custom bot implementations

## Tooling enhancements

**Record/replay testing:**
- Record real Telegram interactions for golden fixture testing
- Replay recorded sessions for regression testing
- Sanitize recorded data for safe test fixtures

**Deterministic testing:**
- Deterministic timestamp support for consistent test results
- Deterministic file ID generation
- Reproducible random data for media testing

**Performance tools:**
- Benchmarking utilities for bot performance
- Load testing simulation with multiple concurrent users
- Memory usage profiling for long-running tests

## Demo UI enhancements

**Reply markup coverage gaps:**
- URL button support — handle `InlineKeyboardButtonUrl` buttons
- Switch inline button support — handle `InlineKeyboardButtonSwitchInlineQuery*` buttons
- Login URL button support — handle `InlineKeyboardButtonLoginUrl` buttons
- Web app button support — handle `InlineKeyboardButtonWebApp` buttons

**Message management:**
- Message edit tracking — distinguish between new messages and edits
- Message history — maintain conversation history in UI
- Message search/filtering — find specific messages in conversation
- Message export — save conversation logs

**Multi-chat support:**
- Multiple chat tabs — test bot in different chat contexts
- Group chat simulation — test with multiple virtual participants
- Channel testing — test bot in broadcast channel context
- Chat switching — seamless switching between different peer types

**Authentication and security:**
- Optional authentication layer — basic auth for shared development
- CORS configuration — configurable cross-origin settings
- Rate limiting — prevent abuse in shared environments
- Access logging — track demo UI usage

**Payments and commerce:**
- Telethon mode payments — implement Stars payment support for real clients
- Payment history — track and review payment interactions
- Multiple payment scenarios — success/failure simulation
- Shipping option testing — for physical goods invoices

## Architecture improvements

**Plugin system:**
- Extensible plugin architecture for custom Bot API methods
- Third-party integrations (payment providers, etc.)
- Custom assertion libraries

**Better error simulation:**
- Network error simulation (timeouts, rate limits)
- Bot API error responses (insufficient permissions, etc.)
- Webhook delivery failure simulation

**Configuration management:**
- Test environment configuration
- Bot behavior customization
- Test data factories and builders