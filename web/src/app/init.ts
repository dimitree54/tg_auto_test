import { initCommandsPanel } from '../features/commands/panel';
import { initFileStaging } from '../features/files/staging';
import { autoStart } from '../flows/autostart';
import { resetDemoConversation } from '../flows/reset';
import { handleSend, sendTextMessage } from '../flows/send';
import { getEls } from '../ui/dom';
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

  void autoStart();
}
