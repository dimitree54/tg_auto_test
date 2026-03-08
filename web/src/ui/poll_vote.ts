import { votePoll } from '../api/bot';
import { failUiTrace, finishUiTrace, startUiTrace } from '../debug/logger';
import { createStreamCallbacks } from '../debug/stream';
import type { MessageResponse } from '../types/api';
import { errorMessage } from '../utils/errors';

import { setInputsDisabled } from './dom';
import { addTextMessage, renderBotResponse } from './messages';
import { hideTyping, showTyping } from './typing';

export async function handlePollVote(messageId: number, optionIds: number[]): Promise<void> {
  const trace = startUiTrace('poll_vote_submitted', { message_id: messageId, option_ids: optionIds });
  try {
    setInputsDisabled(true);
    showTyping();

    await votePoll(
      messageId,
      optionIds,
      trace.id,
      createStreamCallbacks(trace.id, (msg: MessageResponse) => {
        hideTyping();
        renderBotResponse(msg);
      }),
    );
    hideTyping();
    finishUiTrace(trace, { status: 'ok' });
  } catch (error) {
    hideTyping();
    addTextMessage(`[Poll vote failed: ${errorMessage(error)}]`, 'received');
    failUiTrace(trace, error, { message_id: messageId });
  } finally {
    setInputsDisabled(false);
  }
}
