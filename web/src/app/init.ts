import { initCommandsPanel } from '../features/commands/panel';
import { initFileStaging } from '../features/files/staging';
import { handleStart } from '../flows/start';
import { resetDemoConversation } from '../flows/reset';
import { handleSend, sendTextMessage } from '../flows/send';
import { getEls, showNotJoinedState } from '../ui/dom';
import { initReplyKeyboard } from '../ui/keyboards_reply';

export function initApp(): void {
  const hint = document.getElementById('buildHint');
  if (hint) hint.style.display = 'none';

  const els = getEls();

  initReplyKeyboard(async (text: string) => {
    await sendTextMessage(text, { clearInput: false });
  });
  initCommandsPanel(async (text: string) => {
    await sendTextMessage(text, { clearInput: false });
  });
  initFileStaging();

  els.sendBtn.addEventListener('click', () => {
    void handleSend();
  });

  els.inputEl.addEventListener('keydown', (e) => {
    if (e.defaultPrevented) return;
    if (e.key === 'Enter') void handleSend();
  });

  els.resetBtn.addEventListener('click', () => {
    void resetDemoConversation();
  });

  els.startBtn.addEventListener('click', () => {
    void handleStart();
  });

  els.messagesEl.addEventListener('click', (e) => {
    const target = e.target as HTMLElement;
    
    if (target.classList.contains('tg-command')) {
      const command = target.dataset.command;
      if (command) {
        void sendTextMessage(command, { clearInput: true });
      }
    }
    
    if (target.classList.contains('tg-spoiler') && !target.classList.contains('revealed')) {
      target.classList.add('revealed');
    }
  });

  showNotJoinedState();
}
