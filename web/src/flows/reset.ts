import { resetConversation } from '../api/bot';
import { resetCommandsState } from '../features/commands/panel';
import { clearStaged } from '../features/files/staging';
import { getEls } from '../ui/dom';
import { hideReplyKeyboard } from '../ui/keyboards_reply';
import { addTextMessage } from '../ui/messages';
import { errorMessage } from '../utils/errors';

import { autoStart } from './autostart';

export async function resetDemoConversation(): Promise<void> {
  const els = getEls();
  els.resetBtn.disabled = true;
  try {
    await resetConversation();
    els.messagesEl.innerHTML = '<div class="day-divider"><span>Today</span></div>';
    hideReplyKeyboard();
    resetCommandsState();
    clearStaged();
    await autoStart();
  } catch (error) {
    addTextMessage(`[Reset failed: ${errorMessage(error)}]`, 'received');
  }
  els.resetBtn.disabled = false;
}
