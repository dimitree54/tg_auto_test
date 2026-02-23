import { sendMessage } from '../api/bot';
import { refreshBotState } from '../features/commands/panel';
import { addTextMessage, renderBotResponse } from '../ui/messages';
import { hideTyping, showTyping } from '../ui/typing';
import { errorMessage } from '../utils/errors';

export async function autoStart(): Promise<void> {
  showTyping();
  try {
    const data = await sendMessage('/start');
    hideTyping();
    renderBotResponse(data);
    await refreshBotState();
  } catch (error) {
    hideTyping();
    addTextMessage(`[Error: ${errorMessage(error)}]`, 'received');
  }
}
