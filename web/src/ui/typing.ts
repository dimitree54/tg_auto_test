import { getEls } from './dom';

export function showTyping(): void {
  const els = getEls();
  els.typingEl.classList.add('visible');
  els.messagesEl.scrollTop = els.messagesEl.scrollHeight;
}

export function hideTyping(): void {
  const els = getEls();
  els.typingEl.classList.remove('visible');
}
