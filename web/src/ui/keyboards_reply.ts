import { appState } from '../state/app';
import type { ReplyKeyboard } from '../types/api';

import { getEls } from './dom';

let onPress: ((text: string) => Promise<void>) | null = null;

export function initReplyKeyboard(handler: (text: string) => Promise<void>): void {
  onPress = handler;
}

export function showReplyKeyboard(rows: ReplyKeyboard): void {
  const els = getEls();
  els.replyKeyboardEl.innerHTML = '';

  for (const row of rows) {
    const rowEl = document.createElement('div');
    rowEl.className = 'rk-row';

    for (const btnData of row) {
      const btn = document.createElement('button');
      btn.className = 'rk-btn';
      btn.textContent = btnData.text || '?';
      btn.addEventListener('click', () => {
        const text = btn.textContent || '';
        if (!text) return;
        if (appState.sending) return;
        hideReplyKeyboard();
        if (onPress) void onPress(text);
      });
      rowEl.appendChild(btn);
    }

    els.replyKeyboardEl.appendChild(rowEl);
  }

  els.replyKeyboardEl.classList.add('visible');
  els.messagesEl.scrollTop = els.messagesEl.scrollHeight;
}

export function hideReplyKeyboard(): void {
  const els = getEls();
  els.replyKeyboardEl.classList.remove('visible');
  els.replyKeyboardEl.innerHTML = '';
}
