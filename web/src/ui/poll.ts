import { votePoll } from '../api/bot';
import type { MessageResponse } from '../types/api';
import { errorMessage } from '../utils/errors';
import { timeStr } from '../utils/time';

import { getEls, setInputsDisabled } from './dom';
import { addTextMessage } from './messages';
import { hideTyping, showTyping } from './typing';

type BubbleType = 'sent' | 'received';



function scrollBottom(): void {
  const els = getEls();
  els.messagesEl.scrollTop = els.messagesEl.scrollHeight;
}

function createBubble(type: BubbleType): HTMLDivElement {
  const el = document.createElement('div');
  el.className = `message ${type}`;
  if (type === 'received') {
    el.innerHTML = '<div class="sender">Bot</div>';
  }
  return el;
}

export function addPollMessage(data: MessageResponse, type: BubbleType): void {
  const els = getEls();
  const el = createBubble(type);

  // Add poll question as heading
  if (data.poll_question) {
    const questionEl = document.createElement('h4');
    questionEl.className = 'poll-question';
    questionEl.textContent = data.poll_question;
    el.appendChild(questionEl);
  }

  // Add poll options as clickable buttons
  if (data.poll_options && data.message_id) {
    const optionsEl = document.createElement('div');
    optionsEl.className = 'poll-options';

    data.poll_options.forEach((option, index) => {
      const button = document.createElement('button');
      button.className = 'poll-option-btn';
      button.textContent = option.text;
      button.onclick = () => handlePollVote(data.message_id, [index]);
      optionsEl.appendChild(button);
    });

    el.appendChild(optionsEl);
  }

  const meta = document.createElement('span');
  meta.className = 'meta';
  meta.textContent = timeStr();
  el.appendChild(meta);
  els.messagesEl.appendChild(el);
  scrollBottom();
}

async function handlePollVote(messageId: number, optionIds: number[]): Promise<void> {
  
  try {
    setInputsDisabled(true);
    showTyping();

    // Call the API to vote
    const response = await votePoll(messageId, optionIds);

    // Show the bot's response as a text message
    if (response.text) {
      addTextMessage(response.text, 'received');
    }

  } catch (error) {
    errorMessage(`Poll vote failed: ${String(error)}`);
  } finally {
    hideTyping();
    setInputsDisabled(false);
  }
}