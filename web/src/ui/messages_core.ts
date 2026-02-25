import { timeStr } from '../utils/time';

import { getEls } from './dom';

export type BubbleType = 'sent' | 'received';

export function scrollBottom(): void {
  const els = getEls();
  els.messagesEl.scrollTop = els.messagesEl.scrollHeight;
}

export function createBubble(type: BubbleType): HTMLDivElement {
  const el = document.createElement('div');
  el.className = `message ${type}`;
  if (type === 'received') {
    el.innerHTML = '<div class="sender">Bot</div>';
  }
  return el;
}

export function metaHtml(): string {
  return `<span class="meta">${timeStr()}</span>`;
}