import { sendMessage } from '../api/bot';
import { failUiTrace, finishUiTrace, logUiEvent, startUiTrace } from '../debug/logger';
import { createStreamCallbacks } from '../debug/stream';
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
  const trace = startUiTrace('start_clicked', { command: '/start' });
  try {
    await sendMessage(
      '/start',
      trace.id,
      createStreamCallbacks(trace.id, (msg) => {
        hideTyping();
        renderBotResponse(msg);
      }),
    );
    hideTyping();
    logUiEvent('state_refresh_started', {}, trace.id);
    await refreshBotState();
    logUiEvent('state_refresh_completed', {}, trace.id);
    finishUiTrace(trace, { status: 'ok' });
  } catch (error) {
    hideTyping();
    addTextMessage(`[Error: ${errorMessage(error)}]`, 'received');
    failUiTrace(trace, error, { command: '/start' });
  } finally {
    els.startBtn.disabled = false;
  }
}
