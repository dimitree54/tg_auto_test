import { pressCallback } from '../api/bot';
import { failUiTrace, finishUiTrace, startUiTrace } from '../debug/logger';
import { createStreamCallbacks } from '../debug/stream';
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

        const trace = startUiTrace('callback_clicked', { callback_data: cbData, message_id: msgId });
        appState.sending = true;
        setInputsDisabled(true);
        showTyping();
        try {
          await pressCallback(
            msgId,
            cbData,
            trace.id,
            createStreamCallbacks(trace.id, (data) => {
              hideTyping();
              onResponse(data);
            }),
          );
          hideTyping();
          finishUiTrace(trace, { status: 'ok' });
        } catch (error) {
          hideTyping();
          onErrorMessage(`[Callback error: ${errorMessage(error)}]`);
          failUiTrace(trace, error, { callback_data: cbData, message_id: msgId });
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
