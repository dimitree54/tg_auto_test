import { escapeHtml } from '../utils/escape';
import { fmtTime, timeStr } from '../utils/time';

import { getEls } from './dom';
import { BubbleType, createBubble, metaHtml, scrollBottom } from './messages_core';

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