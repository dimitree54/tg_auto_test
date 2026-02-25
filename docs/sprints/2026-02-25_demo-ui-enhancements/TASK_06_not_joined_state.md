---
Task ID: `T6`
Title: `Implement "not yet joined" state with Start button (Issue #8)`
Depends on: T1
Parallelizable: yes, with T4, T5
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Replace the auto-`/start` behavior with a Telegram-like "not yet joined" initial state. The Demo UI opens with an empty chat showing a "No messages here yet..." placeholder and a "Start" button at the bottom (instead of the text input). Pressing "Start" sends `/start` and transitions to normal chat. Reset returns to the "not joined" state.

## Context (contract mapping)

- Requirements: GitHub Issue #8 — "Remove auto /start on Demo UI launch"
- Architecture: frontend flow in `app/init.ts`, `flows/autostart.ts`, `flows/reset.ts`

## Preconditions

- T1 completed: `messages.ts` decomposed (the start button transition will involve the message area, which should be cleanly structured first)

## Non-goals

- No backend changes — "not joined" state is purely frontend
- No changes to API endpoints
- Entity rendering (separate feature — T4/T5)

## Touched surface (expected files / modules)

- `web/src/app/init.ts` — remove `autoStart()` call; add start-button setup
- `web/src/flows/autostart.ts` — DELETE or repurpose into `flows/start.ts`
- `web/src/flows/reset.ts` — update to restore "not joined" state instead of calling autoStart
- `web/src/flows/send.ts` — no changes (send already handles text input normally)
- `web/index.html` — add placeholder element and start button element
- `web/src/ui/dom.ts` — add new element references for placeholder and start button
- `web/src/styles/components/start.css` — NEW: styles for start button and placeholder
- `web/src/styles/index.css` — import start.css

## Dependencies and sequencing notes

- Depends on T1 (messages.ts decomposition) to ensure clean file structure
- Can run in parallel with T4/T5 (entity rendering) — different files
- T7 depends on this task (final verification)

## Third-party / library research (mandatory for any external dependency)

No third-party libraries involved. Pure DOM manipulation and CSS.

- **Telegram UX reference**: When you open a Telegram chat with a bot for the first time, you see the bot's profile info and a large "START" button at the bottom. The chat area shows no messages. After pressing Start, the `/start` command is sent and the normal chat input appears.

## Implementation steps (developer-facing)

1. **Update `web/index.html`** — add placeholder and start button elements:
   
   Inside `.chat-messages` (the `#messages` div), add a placeholder div:
   ```html
   <div class="chat-messages" id="messages">
     <div class="day-divider"><span>Today</span></div>
     <div class="empty-placeholder" id="emptyPlaceholder">No messages here yet...</div>
   </div>
   ```
   
   Add a start button container BEFORE the `.chat-input` div:
   ```html
   <div class="start-container" id="startContainer">
     <button type="button" class="start-btn" id="startBtn">Start</button>
   </div>
   ```
   
   The `.chat-input` div will be initially hidden (via CSS class) and shown after Start is pressed.

2. **Update `web/src/ui/dom.ts`** — add new element references:
   ```typescript
   interface DemoEls {
     // ... existing fields
     emptyPlaceholder: HTMLElement;
     startContainer: HTMLElement;
     startBtn: HTMLButtonElement;
     chatInputEl: HTMLElement;  // the .chat-input container
   }
   ```
   Add to `getEls()`:
   ```typescript
   emptyPlaceholder: requireEl<HTMLElement>('emptyPlaceholder'),
   startContainer: requireEl<HTMLElement>('startContainer'),
   startBtn: requireEl<HTMLButtonElement>('startBtn'),
   chatInputEl: document.querySelector('.chat-input') as HTMLElement,
   ```
   
   **Line count check**: `dom.ts` is currently 51 lines. Adding ~6 lines → ~57 lines ✅

3. **Create UI state management functions** — add to a new file or to `dom.ts`:
   
   Best place: add to `dom.ts` since it's small (51 lines) and these are DOM state functions:
   ```typescript
   export function showNotJoinedState(): void {
     const els = getEls();
     els.emptyPlaceholder.style.display = '';
     els.startContainer.style.display = '';
     els.chatInputEl.style.display = 'none';
   }
   
   export function showActiveState(): void {
     const els = getEls();
     els.emptyPlaceholder.style.display = 'none';
     els.startContainer.style.display = 'none';
     els.chatInputEl.style.display = '';
   }
   ```
   
   `dom.ts` line count: 51 + ~14 = ~65 lines ✅

4. **Delete `web/src/flows/autostart.ts`** — this file is superseded:
   - Currently it auto-sends `/start`, shows typing, renders response
   - This behavior is no longer wanted on launch
   - The Start button will do similar work but triggered by user action

5. **Create `web/src/flows/start.ts`** — new file for the Start button flow:
   ```typescript
   import { sendMessage } from '../api/bot';
   import { refreshBotState } from '../features/commands/panel';
   import { addTextMessage, renderBotResponse } from '../ui/messages';
   import { showActiveState } from '../ui/dom';
   import { hideTyping, showTyping } from '../ui/typing';
   import { errorMessage } from '../utils/errors';
   
   export async function handleStart(): Promise<void> {
     showActiveState();
     addTextMessage('/start', 'sent');
     showTyping();
     try {
       const data = await sendMessage('/start');
       hideTyping();
       renderBotResponse(data);
       await refreshBotState();
     } catch (error) {
       hideTyping();
       addTextMessage(`[Error: ${errorMessage(error)}]`, 'received');
     }
   }
   ```
   
   ~20 lines ✅

6. **Update `web/src/app/init.ts`**:
   - Remove import of `autoStart` from `flows/autostart`
   - Add import of `handleStart` from `flows/start`
   - Add import of `showNotJoinedState` from `ui/dom`
   - Remove `void autoStart();` at the end
   - Add start button click handler:
     ```typescript
     els.startBtn.addEventListener('click', () => {
       void handleStart();
     });
     ```
   - Call `showNotJoinedState()` at the end to set initial state
   - Updated `init.ts` line count: 37 - 2 (remove autostart) + 5 (add start) = ~40 lines ✅

7. **Update `web/src/flows/reset.ts`**:
   - Remove import of `autoStart` from `./autostart`
   - Add import of `showNotJoinedState` from `../ui/dom`
   - Replace `await autoStart();` with `showNotJoinedState();`
   - The reset flow should:
     1. Clear messages
     2. Reset API state
     3. Show "not joined" state (placeholder + start button, hide input)
   - Updated code:
     ```typescript
     export async function resetDemoConversation(): Promise<void> {
       const els = getEls();
       els.resetBtn.disabled = true;
       try {
         await resetConversation();
         els.messagesEl.innerHTML = '<div class="day-divider"><span>Today</span></div><div class="empty-placeholder" id="emptyPlaceholder">No messages here yet...</div>';
         hideReplyKeyboard();
         resetCommandsState();
         clearStaged();
         showNotJoinedState();
       } catch (error) {
         addTextMessage(`[Reset failed: ${errorMessage(error)}]`, 'received');
       }
       els.resetBtn.disabled = false;
     }
     ```
   - **Note**: After reset, the `emptyPlaceholder` element needs to be re-created in the DOM since `messagesEl.innerHTML` replaces all children. The `showNotJoinedState` function reads the element by ID. Two approaches:
     - a) Include the placeholder in the innerHTML string (shown above)
     - b) Reset the cached DOM elements in `getEls()`
   - Approach (a) is simpler. But `getEls()` caches elements — the `emptyPlaceholder` ref becomes stale. Need to handle this by:
     - Either invalidating the cache in `getEls()` after reset
     - Or not caching `emptyPlaceholder` and `startContainer` (query them each time)
     - Or using a different approach: don't destroy and recreate; just hide/show
   - **Better approach**: Don't include placeholder in innerHTML. Instead, keep the placeholder as a permanent DOM element that gets shown/hidden:
     - Don't clear it with innerHTML. Instead, remove only message bubbles and leave structural elements.
     - OR: After innerHTML reset, re-query the placeholder (add a `resetCachedEls()` function or just re-create from scratch)
   
   **Simplest correct approach**: 
   - The placeholder is in the HTML. On reset, set innerHTML to the original HTML (including placeholder). 
   - After innerHTML reset, call a cache-invalidation function on dom.ts so `getEls()` re-queries.
   - Add `resetElsCache()` to `dom.ts`: `export function resetElsCache(): void { cachedEls = null; }`
   - Then in reset.ts: `resetElsCache()` before `showNotJoinedState()`

8. **Create `web/src/styles/components/start.css`**:
   ```css
   .empty-placeholder {
     text-align: center;
     color: #8e9ba7;
     font-size: 14px;
     padding: 32px 16px;
     flex: 1;
     display: flex;
     align-items: center;
     justify-content: center;
   }
   
   .start-container {
     display: flex;
     padding: 12px 16px;
     justify-content: center;
     flex-shrink: 0;
   }
   
   .start-btn {
     background: var(--accent, #075e54);
     color: #fff;
     border: none;
     border-radius: 8px;
     padding: 12px 48px;
     font-size: 16px;
     font-weight: 600;
     cursor: pointer;
     text-transform: uppercase;
     letter-spacing: 0.5px;
     transition: background 0.2s;
   }
   
   .start-btn:hover {
     opacity: 0.9;
   }
   
   .start-btn:disabled {
     background: #aaa;
     cursor: not-allowed;
   }
   ```
   ~40 lines ✅

9. **Update `web/src/styles/index.css`** — add import for start.css

10. **Hide the text input area initially with CSS or JS**:
    - Use `showNotJoinedState()` in init (step 6) — this hides `.chat-input` via `display: none`
    - `showActiveState()` restores it

11. **Also hide placeholder when first message is added**:
    - `showActiveState()` hides the placeholder
    - This is called in `handleStart()` before adding the /start message

12. **Run `make check`** to verify everything works.

## Production safety constraints (mandatory)

- **Database operations**: N/A
- **Resource isolation**: N/A — frontend-only change
- **Migration preparation**: N/A

## Anti-disaster constraints (mandatory)

- **Reuse before build**: reuses existing `sendMessage` API, existing `renderBotResponse`, existing UI patterns
- **Correct libraries only**: no new libraries
- **Correct file locations**: `flows/start.ts` alongside existing `flows/send.ts`, `flows/reset.ts`
- **No regressions**: Reset still works; normal message sending still works after Start
- **Follow UX/spec**: matches Telegram's "not yet joined" UX — empty chat with Start button

## Error handling + correctness rules (mandatory)

- **Do not silence errors**: Start button flow uses same error pattern as autoStart (show error in chat bubble)
- If `/start` command fails, the error is displayed and the UI remains in active state (user can retry via text input)
- Start button is disabled during the send to prevent double-clicks

## Zero legacy tolerance rule (mandatory)

After implementing this task:
- `autostart.ts` is DELETED — no parallel old/new paths
- No dead imports referencing `autostart.ts`
- Reset flow goes to "not joined" state, not auto-start
- `flows/start.ts` replaces `flows/autostart.ts` completely

## Acceptance criteria (testable)

1. Demo UI opens with empty chat showing "No messages here yet..." placeholder
2. Start button is visible at the bottom; text input is hidden
3. Clicking Start sends `/start` command to the bot
4. After Start, placeholder disappears, Start button disappears, text input appears
5. Bot response to `/start` is rendered in the chat
6. Reset button returns to "not joined" state (placeholder + start button visible, input hidden, messages cleared)
7. `autostart.ts` file is deleted
8. No import references to `autostart.ts` remain in the codebase
9. All files remain under 200 lines
10. `make check` passes

## Verification / quality gates

- [ ] Unit tests added/updated — N/A (frontend interaction; no backend changes)
- [ ] Linters/formatters pass — `make check` green
- [ ] No new warnings introduced
- [ ] Negative-path tests — error during /start is shown in chat bubble

## Edge cases

- User clicks Start while previous request is in-flight — button should be disabled during the request
- `/start` command fails (bot not running) — error shown in chat, UI stays in active state so user can retry
- Reset during active chat — should clear all messages and return to not-joined state
- Multiple rapid resets — debounced by `resetBtn.disabled = true` during reset
- DOM cache invalidation after reset — `resetElsCache()` ensures fresh element references

## Notes / risks

- **Risk**: DOM cache invalidation in `dom.ts` is a new pattern that could affect other code
  - **Mitigation**: `resetElsCache()` is only called in `reset.ts` after innerHTML replacement; all other code paths don't affect the cached elements
- **Risk**: CSS `display: none` on `.chat-input` might conflict with other visibility logic
  - **Mitigation**: `showActiveState()` / `showNotJoinedState()` are the only places controlling this visibility
