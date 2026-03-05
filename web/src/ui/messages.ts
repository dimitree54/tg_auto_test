import type { MessageResponse, MessageEntity } from '../types/api';
import { escapeHtml } from '../utils/escape';
import { renderEntities } from '../utils/formatting';

import { getEls } from './dom';
import { addInvoiceMessage } from './invoice';
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
    addInvoiceMessage(data, 'received', {
      onErrorText: (text) => addTextMessage(text, 'received'),
      onResponse: renderBotResponse,
    });
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
