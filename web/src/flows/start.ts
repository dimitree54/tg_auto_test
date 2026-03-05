import { sendMessage } from '../api/bot';
import { refreshBotState } from '../features/commands/panel';
import { addTextMessage, renderBotResponse } from '../ui/messages';
import { getEls, showActiveState } from '../ui/dom';
import { hideTyping, showTyping } from '../ui/typing';
import { errorMessage } from '../utils/errors';

export async function handleStart(): Promise<void> {
  const els = getEls();
  els.startBtn.disabled = true;
  
  showActiveState();
  addTextMessage('/start', 'sent');
  showTyping();
  try {
    let gotFirst = false;
    await sendMessage('/start', (msg) => {
      if (!gotFirst) {
        hideTyping();
        gotFirst = true;
      }
      renderBotResponse(msg);
    });
    if (!gotFirst) hideTyping();
    await refreshBotState();
  } catch (error) {
    hideTyping();
    addTextMessage(`[Error: ${errorMessage(error)}]`, 'received');
  } finally {
    els.startBtn.disabled = false;
  }
}