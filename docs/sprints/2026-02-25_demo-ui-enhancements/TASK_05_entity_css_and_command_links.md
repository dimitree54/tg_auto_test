---
Task ID: `T5`
Title: `Add entity CSS styles and clickable /command links`
Depends on: T4
Parallelizable: yes, with T6
Owner: Developer (Scrum Master plans only)
Status: `planned`
---

## Goal / value

Complete the entity rendering feature with CSS styles for spoilers, code blocks, and pre blocks, and make `/command` patterns in bot message text clickable (sends the command to chat when clicked).

## Context (contract mapping)

- Requirements: GitHub Issue #9 — "Frontend CSS: Add styles for `.tg-spoiler`, `code` inline, `pre` block"
- Requirements: GitHub Issue #9 comment — "make `/command` in text a clickable link that sends the command to chat"

## Preconditions

- T4 completed: entity renderer exists, `renderEntities()` wired into message display

## Non-goals

- No changes to backend
- No changes to entity rendering algorithm (that's in T4)

## Touched surface (expected files / modules)

- `web/src/styles/components/entities.css` — NEW: styles for entity HTML elements
- `web/src/styles/index.css` — import the new CSS file
- `web/src/utils/formatting.ts` — add `/command` detection and clickable link generation
- `web/src/ui/messages.ts` — add click handler for command links in bot messages

## Dependencies and sequencing notes

- Depends on T4 (entity renderer must exist; CSS targets the HTML it produces)
- Can run in parallel with T6 (different files except potentially messages.ts)
- T7 depends on this task

## Third-party / library research (mandatory for any external dependency)

- **Telegram spoiler behavior**: On Telegram, spoilers show blurred/obscured text that reveals on click/tap. For the demo UI, a simple CSS approach: initially blurred with `filter: blur(5px)` or `color: transparent; background-color: currentColor`, and on click toggle a `.revealed` class.
  - Reference: Telegram Web/Desktop behavior — spoiler text is initially hidden, revealed on click
  
- **CSS `filter: blur()`**: Supported in all modern browsers
  - Reference: https://developer.mozilla.org/en-US/docs/Web/CSS/filter — `filter: blur(5px)`

- **Telegram command pattern**: Commands start with `/`, followed by letters/digits/underscores, 1-32 chars. Regex: `/\/[a-zA-Z0-9_]{1,32}(?=\s|$)/g`
  - Reference: Telegram Bot API — https://core.telegram.org/bots/api#messageentity — `bot_command` entity type

## Implementation steps (developer-facing)

1. **Create `web/src/styles/components/entities.css`**:
   ```css
   /* Telegram entity styles */
   
   /* Spoiler — initially hidden, click to reveal */
   .tg-spoiler {
     background-color: currentColor;
     border-radius: 2px;
     cursor: pointer;
     transition: background-color 0.3s;
   }
   
   .tg-spoiler.revealed {
     background-color: transparent;
   }
   
   /* Inline code */
   .message code {
     background: rgba(0, 0, 0, 0.06);
     padding: 1px 4px;
     border-radius: 3px;
     font-family: 'SFMono-Regular', 'Consolas', 'Liberation Mono', 'Menlo', monospace;
     font-size: 13px;
   }
   
   /* Code block */
   .message pre {
     background: rgba(0, 0, 0, 0.06);
     padding: 8px 12px;
     border-radius: 6px;
     overflow-x: auto;
     font-family: 'SFMono-Regular', 'Consolas', 'Liberation Mono', 'Menlo', monospace;
     font-size: 13px;
     white-space: pre-wrap;
     word-wrap: break-word;
     margin: 4px 0;
   }
   
   .message pre code {
     background: none;
     padding: 0;
     border-radius: 0;
   }
   
   /* Links in bot messages */
   .message.received a {
     color: #2678b6;
     text-decoration: none;
   }
   
   .message.received a:hover {
     text-decoration: underline;
   }
   
   /* Command links */
   .tg-command {
     color: #2678b6;
     cursor: pointer;
     text-decoration: none;
   }
   
   .tg-command:hover {
     text-decoration: underline;
   }
   ```
   
   Estimated: ~60 lines ✅

2. **Update `web/src/styles/index.css`** — add import:
   ```css
   @import './components/entities.css';
   ```

3. **Add `/command` link rendering to `web/src/utils/formatting.ts`**:
   
   After entity rendering, process the resulting HTML to find bare `/command` patterns (those NOT already inside entity-rendered content) and wrap them in clickable spans.
   
   **Approach**: Add command detection as part of the entity rendering itself. When `renderEntities` processes plain text segments (text not covered by any entity), scan for `/command` patterns and wrap them:
   ```typescript
   function escapeAndLinkCommands(text: string): string {
     // Split text by /command patterns, escape each part, wrap commands
     const commandPattern = /\/([a-zA-Z0-9_]{1,32})(?=\s|$)/g;
     let result = '';
     let lastIndex = 0;
     let match: RegExpExecArray | null;
     
     while ((match = commandPattern.exec(text)) !== null) {
       // Escape text before the command
       result += escapeHtml(text.slice(lastIndex, match.index));
       // Wrap command in clickable span
       result += `<span class="tg-command" data-command="${escapeHtml(match[0])}">${escapeHtml(match[0])}</span>`;
       lastIndex = match.index + match[0].length;
     }
     
     // Escape remaining text
     result += escapeHtml(text.slice(lastIndex));
     return result;
   }
   ```
   
   Then in `renderEntities`, replace `escapeHtml(text.slice(...))` calls for plain text segments with `escapeAndLinkCommands(text.slice(...))`.
   
   **Important**: Only apply command linking in plain text segments (not inside `<code>` or `<pre>` entities — commands in code blocks should NOT be clickable).

4. **Add click handler for command links in `web/src/ui/messages.ts`**:
   
   Use event delegation on the messages container:
   ```typescript
   // In initApp or where messages container is set up
   els.messagesEl.addEventListener('click', (e) => {
     const target = e.target as HTMLElement;
     if (target.classList.contains('tg-command')) {
       const command = target.dataset.command;
       if (command) {
         void sendTextMessage(command, { clearInput: true });
       }
     }
   });
   ```
   
   **Where to place this**: The click handler should be in `messages.ts` or in `app/init.ts` since it involves message sending. Best place: `app/init.ts` (where other event listeners are set up), importing `sendTextMessage` which is already imported there.

5. **Add spoiler click-to-reveal handler**:
   
   Use event delegation on the messages container:
   ```typescript
   els.messagesEl.addEventListener('click', (e) => {
     const target = e.target as HTMLElement;
     if (target.classList.contains('tg-spoiler') && !target.classList.contains('revealed')) {
       target.classList.add('revealed');
     }
   });
   ```
   
   Place in `app/init.ts` alongside the command link handler.

6. **File size checks**:
   - `entities.css`: ~60 lines ✅
   - `formatting.ts`: was ~80-120 from T4, adding ~25 lines for command linking → ~105-145 lines ✅
   - `messages.ts`: no changes beyond T4
   - `app/init.ts`: currently 37 lines, adding ~15 lines for event handlers → ~52 lines ✅

7. **Run `make check`** to verify everything passes.

## Production safety constraints (mandatory)

- **Database operations**: N/A
- **Resource isolation**: N/A — frontend-only changes
- **Migration preparation**: N/A

## Anti-disaster constraints (mandatory)

- **Reuse before build**: event delegation pattern already used in `app/init.ts` for send/reset buttons
- **Correct libraries only**: no new libraries — pure CSS and DOM
- **Correct file locations**: CSS in `web/src/styles/components/` (existing pattern), JS in existing files
- **No regressions**: new CSS only targets new classes/elements; no existing styles overridden
- **Follow UX/spec**: spoiler behavior matches Telegram's click-to-reveal; command links match Telegram's clickable commands

## Error handling + correctness rules (mandatory)

- **Do not silence errors**: command click handler validates `data-command` exists before sending
- No try/catch needed — event handlers delegate to existing `sendTextMessage` which has its own error handling
- Invalid command patterns won't match the regex, so no false positives

## Zero legacy tolerance rule (mandatory)

After implementing this task:
- No unstyled entity elements (all entity types have CSS coverage)
- No dead CSS rules
- Command links are functional (not just visual)

## Acceptance criteria (testable)

1. `web/src/styles/components/entities.css` exists with styles for `.tg-spoiler`, `code`, `pre`, `.tg-command`
2. `entities.css` is imported in `index.css`
3. Spoiler text is visually hidden initially (blurred/obscured)
4. Clicking a spoiler reveals the text (adds `.revealed` class)
5. Inline `code` has distinct background and monospace font
6. `pre` blocks have distinct background, padding, and monospace font
7. `/command` patterns in plain text of bot messages are wrapped in clickable `.tg-command` spans
8. Clicking a command link sends the command text to the chat
9. Commands inside `<code>` or `<pre>` blocks are NOT made clickable
10. All files remain under 200 lines
11. `make check` passes

## Verification / quality gates

- [ ] Unit tests added/updated — manual browser testing for CSS and interaction
- [ ] Linters/formatters pass — `make check` green
- [ ] No new warnings introduced
- [ ] Negative-path tests — N/A for CSS

## Edge cases

- Spoiler already revealed — clicking again does nothing (already has `.revealed` class)
- Command at end of message without trailing whitespace — regex lookahead handles `$`
- Command with maximum length (32 chars) — regex captures correctly
- Command-like patterns inside code blocks — must NOT be linkified (handled by only processing plain text segments)
- Multiple commands in one message — each gets its own clickable span
- `/@username` — not a command pattern; regex only matches `/[a-zA-Z0-9_]`

## Notes / risks

- **Risk**: CSS specificity conflicts with existing message styles
  - **Mitigation**: New styles use `.message` parent selector for proper scoping
- **Risk**: Command regex might be too greedy or too restrictive
  - **Mitigation**: Follows Telegram's official bot_command entity specification (1-32 chars, alphanumeric + underscore)
