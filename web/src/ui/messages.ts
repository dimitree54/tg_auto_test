import { payInvoice } from '../api/bot';
import { appState } from '../state/app';
import type { MessageResponse, MessageEntity } from '../types/api';
import { errorMessage } from '../utils/errors';
import { escapeHtml } from '../utils/escape';
import { renderEntities } from '../utils/formatting';
import { timeStr } from '../utils/time';

import { getEls, setInputsDisabled } from './dom';
import { addInlineKeyboard } from './keyboards_inline';
import { showReplyKeyboard } from './keyboards_reply';
import { BubbleType, createBubble, findBubbleByMessageId, metaHtml, scrollBottom } from './messages_core';
import {
  addAudioMessage,
  addDocumentMessage,
  addPhotoMessage,
  addVideoNoteMessage,
} from './messages_media';
import { addPollMessage } from './poll';
import { hideTyping, showTyping } from './typing';

export function addTextMessage(text: string, type: BubbleType, entities?: MessageEntity[], messageId?: number): void {
  const els = getEls();
  const el = createBubble(type, messageId);
  const content = type === 'received' && entities?.length
    ? renderEntities(text, entities)
    : escapeHtml(text);
  el.innerHTML += `<span class="text">${content}</span>${metaHtml()}`;
  els.messagesEl.appendChild(el);
  scrollBottom();
}

function invoiceAmountLabel(currency: string, totalAmount: number): string {
  if (currency === 'XTR') return `${totalAmount}${totalAmount === 1 ? ' Star' : ' Stars'}`;
  return `${totalAmount} ${currency}`;
}

function addInvoiceMessage(data: MessageResponse, type: BubbleType): void {
  const els = getEls();
  const el = createBubble(type);
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
    appState.sending = true;
    setInputsDisabled(true);
    payBtn.disabled = true;
    payBtn.textContent = 'Paying...';
    showTyping();
    try {
      const respData = await payInvoice(data.message_id);
      hideTyping();
      payBtn.textContent = 'Paid';
      renderBotResponse(respData);
    } catch (error) {
      hideTyping();
      payBtn.disabled = false;
      payBtn.textContent = `Pay ${invoiceAmountLabel(currency, totalAmount)}`;
      addTextMessage(`[Payment error: ${errorMessage(error)}]`, 'received');
    }
    appState.sending = false;
    setInputsDisabled(false);
    els.inputEl.focus();
  });
  card.appendChild(payBtn);

  el.appendChild(card);
  const meta = document.createElement('span');
  meta.className = 'meta';
  meta.textContent = timeStr();
  el.appendChild(meta);
  els.messagesEl.appendChild(el);
  scrollBottom();
}

function updateBubbleInPlace(existing: HTMLDivElement, data: MessageResponse): void {
  const content = renderEntities(data.text || '', data.entities ?? []);
  const markup = data.reply_markup || null;

  // Preserve sender div, replace everything else
  existing.innerHTML = '<div class="sender">Bot</div>';
  existing.innerHTML += `<span class="text">${content}</span>${metaHtml()}`;

  if (markup && markup.inline_keyboard) {
    addInlineKeyboard(existing, markup.inline_keyboard, data.message_id, renderBotResponse, (text) =>
      addTextMessage(text, 'received'),
    );
  }

  scrollBottom();
}

export function renderBotResponse(data: MessageResponse): void {
  const els = getEls();
  const markup = data.reply_markup || null;

  // Handle edit: update existing message in-place
  if (data.is_edit && data.type === 'text') {
    const existing = findBubbleByMessageId(data.message_id);
    if (existing) {
      updateBubbleInPlace(existing, data);
      return;
    }
  }

  if (data.type === 'text') {
    if (markup && markup.inline_keyboard) {
      const el = createBubble('received', data.message_id);
      const content = renderEntities(data.text || '', data.entities ?? []);
      el.innerHTML += `<span class="text">${content}</span>${metaHtml()}`;
      els.messagesEl.appendChild(el);
      addInlineKeyboard(el, markup.inline_keyboard, data.message_id, renderBotResponse, (text) =>
        addTextMessage(text, 'received'),
      );
      scrollBottom();
    } else {
      addTextMessage(data.text || '', 'received', data.entities, data.message_id);
    }
    if (markup && markup.keyboard) showReplyKeyboard(markup.keyboard);
    return;
  }

  if (data.type === 'invoice') {
    addInvoiceMessage(data, 'received');
    return;
  }

  if (data.type === 'photo') {
    addPhotoMessage(`/api/file/${data.file_id || ''}`, 'received', data.text || undefined, data.entities);
    return;
  }

  if (data.type === 'voice') {
    addAudioMessage(`/api/file/${data.file_id || ''}`, 'received', data.text || undefined, data.entities);
    return;
  }

  if (data.type === 'video_note') {
    addVideoNoteMessage(`/api/file/${data.file_id || ''}`, 'received', data.text || undefined, data.entities);
    return;
  }

  if (data.type === 'document') {
    addDocumentMessage(data.filename || '', `/api/file/${data.file_id || ''}`, 'received', data.text || undefined, data.entities);
    return;
  }

  if (data.type === 'poll') {
    addPollMessage(data, 'received');
    return;
  }

  addTextMessage(`[Unknown response type: ${data.type}]`, 'received');
}

export { addAudioMessage, addDocumentMessage, addPhotoMessage, addVideoNoteMessage } from './messages_media';
