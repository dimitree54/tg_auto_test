import type { MessageResponse } from '../types/api';
import { timeStr } from '../utils/time';

import { getEls } from './dom';
import { createBubble, scrollBottom } from './messages_core';
import { handlePollVote } from './poll_vote';

type BubbleType = 'sent' | 'received';

export function addPollMessage(data: MessageResponse, type: BubbleType): void {
  const els = getEls();
  const el = createBubble(type, data.message_id);

  if (data.poll_question) {
    const q = document.createElement('div');
    q.className = 'poll-question';
    q.textContent = data.poll_question;
    el.appendChild(q);

    const label = document.createElement('div');
    label.className = 'poll-type-label';
    label.textContent = 'Poll';
    el.appendChild(label);
  }

  if (data.poll_options && data.message_id) {
    const optionsEl = document.createElement('div');
    optionsEl.className = 'poll-options';

    data.poll_options.forEach((option, index) => {
      const row = document.createElement('div');
      row.className = 'poll-option-row';
      row.textContent = option.text;
      row.onclick = () => {
        showResults(el, data, index);
        handlePollVote(data.message_id, [index]);
      };
      optionsEl.appendChild(row);
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

function showResults(bubble: HTMLElement, data: MessageResponse, selectedIndex: number): void {
  const container = bubble.querySelector('.poll-options');
  if (!container || !data.poll_options) return;

  container.innerHTML = '';
  data.poll_options.forEach((option, i) => {
    const isSelected = i === selectedIndex;
    const percent = isSelected ? 100 : 0;

    const row = document.createElement('div');
    row.className = 'poll-result-row';

    const header = document.createElement('div');
    header.className = 'poll-result-header';

    const marker = document.createElement('div');
    marker.className = isSelected ? 'poll-check' : 'poll-dot';
    if (isSelected) marker.textContent = '\u2713';
    header.appendChild(marker);

    const pctEl = document.createElement('span');
    pctEl.className = 'poll-result-pct';
    pctEl.textContent = `${percent}%`;
    header.appendChild(pctEl);

    const text = document.createElement('span');
    text.className = 'poll-result-text';
    text.textContent = option.text;
    header.appendChild(text);

    row.appendChild(header);

    const track = document.createElement('div');
    track.className = 'poll-result-bar-track';
    const fill = document.createElement('div');
    fill.className = 'poll-result-bar-fill';
    fill.style.width = '0%';
    track.appendChild(fill);
    row.appendChild(track);

    container.appendChild(row);

    requestAnimationFrame(() => {
      fill.style.width = `${percent}%`;
    });
  });
}
