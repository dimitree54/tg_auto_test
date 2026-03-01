import { timeStr } from '../utils/time';

import { getEls } from './dom';

export type BubbleType = 'sent' | 'received';

export function scrollBottom(): void {
  const els = getEls();
  els.messagesEl.scrollTop = els.messagesEl.scrollHeight;
}

export function createBubble(type: BubbleType, messageId?: number): HTMLDivElement {
  const el = document.createElement('div');
  el.className = `message ${type}`;
  if (type === 'received') {
    el.innerHTML = '<div class="sender">Bot</div>';
  }
  if (messageId !== undefined) {
    el.dataset.messageId = String(messageId);
  }
  return el;
}

export function findBubbleByMessageId(messageId: number): HTMLDivElement | null {
  const els = getEls();
  return els.messagesEl.querySelector<HTMLDivElement>(
    `.message[data-message-id="${messageId}"]`,
  );
}

export function metaHtml(): string {
  return `<span class="meta">${timeStr()}</span>`;
}