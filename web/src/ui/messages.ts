import { payInvoice } from '../api/bot';
import { appState } from '../state/app';
import type { MessageResponse } from '../types/api';
import { errorMessage } from '../utils/errors';
import { escapeHtml } from '../utils/escape';
import { fmtTime, timeStr } from '../utils/time';

import { getEls, setInputsDisabled } from './dom';
import { addInlineKeyboard } from './keyboards_inline';
import { showReplyKeyboard } from './keyboards_reply';
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

function metaHtml(): string {
  return `<span class="meta">${timeStr()}</span>`;
}

export function addTextMessage(text: string, type: BubbleType): void {
  const els = getEls();
  const el = createBubble(type);
  el.innerHTML += `<span class="text">${escapeHtml(text)}</span>${metaHtml()}`;
  els.messagesEl.appendChild(el);
  scrollBottom();
}

export function addPhotoMessage(src: string, type: BubbleType, caption?: string): void {
  const els = getEls();
  const el = createBubble(type);
  const img = document.createElement('img');
  img.className = 'msg-photo';
  img.src = src;
  img.alt = 'Photo';
  el.appendChild(img);
  if (caption) el.innerHTML += `<span class="caption">${escapeHtml(caption)}</span>`;
  el.innerHTML += metaHtml();
  els.messagesEl.appendChild(el);
  img.addEventListener('load', () => scrollBottom());
  scrollBottom();
}

export function addAudioMessage(src: string, type: BubbleType, caption?: string): void {
  const els = getEls();
  const el = createBubble(type);

  const player = document.createElement('div');
  player.className = 'voice-player';

  const audio = document.createElement('audio');
  audio.src = src;
  audio.preload = 'metadata';

  const playBtn = document.createElement('button');
  playBtn.className = 'vp-play';
  playBtn.innerHTML = '&#9654;';

  const track = document.createElement('div');
  track.className = 'vp-track';

  const bar = document.createElement('div');
  bar.className = 'vp-bar';
  const fill = document.createElement('div');
  fill.className = 'vp-fill';
  bar.appendChild(fill);

  const timeLabel = document.createElement('span');
  timeLabel.className = 'vp-time';
  timeLabel.textContent = '0:00';

  track.appendChild(bar);
  track.appendChild(timeLabel);
  player.appendChild(playBtn);
  player.appendChild(track);
  el.appendChild(player);

  if (caption) {
    const cap = document.createElement('span');
    cap.className = 'caption';
    cap.textContent = caption;
    el.appendChild(cap);
  }

  const meta = document.createElement('span');
  meta.className = 'meta';
  meta.textContent = timeStr();
  el.appendChild(meta);
  els.messagesEl.appendChild(el);

  audio.addEventListener('loadedmetadata', () => {
    timeLabel.textContent = fmtTime(audio.duration);
  });

  playBtn.addEventListener('click', () => {
    if (audio.paused) {
      void audio.play();
      playBtn.innerHTML = '&#9646;&#9646;';
    } else {
      audio.pause();
      playBtn.innerHTML = '&#9654;';
    }
  });

  audio.addEventListener('timeupdate', () => {
    if (audio.duration) {
      const pct = (audio.currentTime / audio.duration) * 100;
      fill.style.width = `${pct}%`;
      timeLabel.textContent = fmtTime(audio.currentTime);
    }
  });

  audio.addEventListener('ended', () => {
    playBtn.innerHTML = '&#9654;';
    fill.style.width = '0%';
    timeLabel.textContent = fmtTime(audio.duration);
  });

  bar.addEventListener('click', (e: MouseEvent) => {
    if (audio.duration) {
      const rect = bar.getBoundingClientRect();
      const ratio = (e.clientX - rect.left) / rect.width;
      audio.currentTime = ratio * audio.duration;
    }
  });

  scrollBottom();
}

export function addVideoNoteMessage(src: string, type: BubbleType, caption?: string): void {
  const els = getEls();
  const el = createBubble(type);
  const video = document.createElement('video');
  video.className = 'msg-video-note';
  video.src = src;
  video.controls = true;
  video.playsInline = true;
  el.appendChild(video);
  if (caption) el.innerHTML += `<span class="caption">${escapeHtml(caption)}</span>`;
  el.innerHTML += metaHtml();
  els.messagesEl.appendChild(el);
  scrollBottom();
}

export function addDocumentMessage(
  filename: string,
  downloadUrl: string | null,
  type: BubbleType,
  caption?: string,
): void {
  const els = getEls();
  const el = createBubble(type);
  const a = document.createElement('a');
  a.className = 'doc-attachment';
  a.href = downloadUrl ? `${downloadUrl}?download=1` : '#';
  a.download = filename || '';
  a.innerHTML = `<span class="doc-icon">&#128196;</span><span class="doc-name">${escapeHtml(filename)}</span>`;
  el.appendChild(a);
  if (caption) el.innerHTML += `<span class="caption">${escapeHtml(caption)}</span>`;
  el.innerHTML += metaHtml();
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

export function renderBotResponse(data: MessageResponse): void {
  const els = getEls();
  const markup = data.reply_markup || null;

  if (data.type === 'text') {
    if (markup && markup.inline_keyboard) {
      const el = createBubble('received');
      el.innerHTML += `<span class="text">${escapeHtml(data.text || '')}</span>${metaHtml()}`;
      els.messagesEl.appendChild(el);
      addInlineKeyboard(el, markup.inline_keyboard, data.message_id, renderBotResponse, (text) =>
        addTextMessage(text, 'received'),
      );
      scrollBottom();
    } else {
      addTextMessage(data.text || '', 'received');
    }
    if (markup && markup.keyboard) showReplyKeyboard(markup.keyboard);
    return;
  }

  if (data.type === 'invoice') {
    addInvoiceMessage(data, 'received');
    return;
  }

  if (data.type === 'photo') {
    addPhotoMessage(`/api/file/${data.file_id || ''}`, 'received');
    return;
  }

  if (data.type === 'voice') {
    addAudioMessage(`/api/file/${data.file_id || ''}`, 'received');
    return;
  }

  if (data.type === 'video_note') {
    addVideoNoteMessage(`/api/file/${data.file_id || ''}`, 'received');
    return;
  }

  if (data.type === 'document') {
    addDocumentMessage(data.filename || '', `/api/file/${data.file_id || ''}`, 'received');
    return;
  }

  addTextMessage(`[Unknown response type: ${data.type}]`, 'received');
}
