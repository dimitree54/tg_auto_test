import { resetConversation } from '../api/bot';
import { failUiTrace, finishUiTrace, startUiTrace } from '../debug/logger';
import { resetCommandsState } from '../features/commands/panel';
import { clearStaged } from '../features/files/staging';
import { getEls, resetElsCache, showNotJoinedState } from '../ui/dom';
import { hideReplyKeyboard } from '../ui/keyboards_reply';
import { addTextMessage } from '../ui/messages';
import { errorMessage } from '../utils/errors';

export async function resetDemoConversation(): Promise<void> {
  const els = getEls();
  els.resetBtn.disabled = true;
  const trace = startUiTrace('reset_clicked');
  try {
    await resetConversation();
    els.messagesEl.innerHTML = '<div class="day-divider"><span>Today</span></div><div class="empty-placeholder" id="emptyPlaceholder">No messages here yet...</div>';
    hideReplyKeyboard();
    resetCommandsState();
    clearStaged();
    resetElsCache();
    showNotJoinedState();
    finishUiTrace(trace, { status: 'ok' });
  } catch (error) {
    addTextMessage(`[Reset failed: ${errorMessage(error)}]`, 'received');
    failUiTrace(trace, error);
  }
  els.resetBtn.disabled = false;
}
