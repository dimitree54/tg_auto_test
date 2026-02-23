import { pressCallback } from '../api/bot';
import { appState } from '../state/app';
import type { InlineKeyboard, MessageResponse } from '../types/api';
import { errorMessage } from '../utils/errors';

import { getEls, setInputsDisabled } from './dom';
import { hideTyping, showTyping } from './typing';

export function addInlineKeyboard(
  parentEl: HTMLElement,
  rows: InlineKeyboard,
  messageId: number,
  onResponse: (data: MessageResponse) => void,
  onErrorMessage: (text: string) => void,
): void {
  const container = document.createElement('div');
  container.className = 'inline-keyboard';

  for (const row of rows) {
    const rowEl = document.createElement('div');
    rowEl.className = 'ik-row';

    for (const btnData of row) {
      const btn = document.createElement('button');
      btn.className = 'ik-btn';
      btn.textContent = btnData.text || '?';
      btn.dataset.callbackData = btnData.callback_data || '';
      btn.dataset.messageId = String(messageId);
      btn.addEventListener('click', async () => {
        const cbData = btn.dataset.callbackData || '';
        const msgId = Number.parseInt(btn.dataset.messageId || '0', 10);
        if (!cbData || appState.sending) return;

        const keyboard = btn.closest('.inline-keyboard');
        const allBtns = keyboard ? keyboard.querySelectorAll<HTMLButtonElement>('.ik-btn') : [];
        for (const b of allBtns) b.disabled = true;

        appState.sending = true;
        setInputsDisabled(true);
        showTyping();
        try {
          const data = await pressCallback(msgId, cbData);
          hideTyping();
          onResponse(data);
        } catch (error) {
          hideTyping();
          onErrorMessage(`[Callback error: ${errorMessage(error)}]`);
        }
        appState.sending = false;
        setInputsDisabled(false);
        getEls().inputEl.focus();
      });
      rowEl.appendChild(btn);
    }

    container.appendChild(rowEl);
  }

  parentEl.appendChild(container);
}
