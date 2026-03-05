import { payInvoice } from '../api/bot';
import { startUiTrace, failUiTrace, finishUiTrace } from '../debug/logger';
import { createStreamCallbacks } from '../debug/stream';
import { appState } from '../state/app';
import type { MessageResponse } from '../types/api';
import { errorMessage } from '../utils/errors';
import { timeStr } from '../utils/time';

import { getEls, setInputsDisabled } from './dom';
import { hideTyping, showTyping } from './typing';

type BubbleType = 'sent' | 'received';

interface InvoiceHandlers {
  onErrorText: (text: string) => void;
  onResponse: (message: MessageResponse) => void;
}

function invoiceAmountLabel(currency: string, totalAmount: number): string {
  if (currency === 'XTR') return `${totalAmount}${totalAmount === 1 ? ' Star' : ' Stars'}`;
  return `${totalAmount} ${currency}`;
}

function appendInvoiceBubble(
  card: HTMLElement,
  type: BubbleType,
): void {
  const els = getEls();
  const el = document.createElement('div');
  el.className = `message ${type}`;
  if (type === 'received') el.innerHTML = '<div class="sender">Bot</div>';
  el.appendChild(card);
  const meta = document.createElement('span');
  meta.className = 'meta';
  meta.textContent = timeStr();
  el.appendChild(meta);
  els.messagesEl.appendChild(el);
  els.messagesEl.scrollTop = els.messagesEl.scrollHeight;
}

export function addInvoiceMessage(
  data: MessageResponse,
  type: BubbleType,
  handlers: InvoiceHandlers,
): void {
  const card = document.createElement('div');
  card.className = 'invoice-card';

  const title = document.createElement('div');
  title.className = 'invoice-title';
  title.textContent = data.title || 'Invoice';
  card.appendChild(title);

  if (data.description) {
    const desc = document.createElement('div');
    desc.className = 'invoice-desc';
    desc.textContent = data.description;
    card.appendChild(desc);
  }

  const currency = data.currency || '';
  const totalAmount = data.total_amount ?? 0;

  const amount = document.createElement('div');
  amount.className = 'invoice-amount';
  amount.textContent = invoiceAmountLabel(currency, totalAmount);
  card.appendChild(amount);

  const payBtn = document.createElement('button');
  payBtn.className = 'invoice-pay';
  payBtn.textContent = `Pay ${invoiceAmountLabel(currency, totalAmount)}`;
  payBtn.addEventListener('click', async () => {
    if (appState.sending) return;
    const trace = startUiTrace('invoice_pay_clicked', { message_id: data.message_id });
    appState.sending = true;
    setInputsDisabled(true);
    payBtn.disabled = true;
    payBtn.textContent = 'Paying...';
    showTyping();
    try {
      await payInvoice(
        data.message_id,
        trace.id,
        createStreamCallbacks(trace.id, (message) => {
          hideTyping();
          handlers.onResponse(message);
        }),
      );
      hideTyping();
      payBtn.textContent = 'Paid';
      finishUiTrace(trace, { status: 'ok' });
    } catch (error) {
      hideTyping();
      payBtn.disabled = false;
      payBtn.textContent = `Pay ${invoiceAmountLabel(currency, totalAmount)}`;
      handlers.onErrorText(`[Payment error: ${errorMessage(error)}]`);
      failUiTrace(trace, error, { message_id: data.message_id });
    }
    appState.sending = false;
    setInputsDisabled(false);
    getEls().inputEl.focus();
  });
  card.appendChild(payBtn);

  appendInvoiceBubble(card, type);
}
