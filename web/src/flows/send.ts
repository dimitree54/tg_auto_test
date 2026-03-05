import { sendFile, sendMessage } from '../api/bot';
import { closeCommandPanel, refreshBotState } from '../features/commands/panel';
import { consumeStagedFiles } from '../features/files/staging';
import { appState } from '../state/app';
import type { FileUploadType } from '../types/api';
import { getEls, setInputsDisabled } from '../ui/dom';
import {
  addAudioMessage,
  addDocumentMessage,
  addPhotoMessage,
  addTextMessage,
  addVideoNoteMessage,
  renderBotResponse,
} from '../ui/messages';
import { hideTyping, showTyping } from '../ui/typing';
import { errorMessage } from '../utils/errors';

export async function sendTextMessage(
  text: string,
  opts?: { clearInput?: boolean },
): Promise<void> {
  const els = getEls();
  const clearInput = opts?.clearInput ?? false;
  if (!text || appState.sending) return;

  closeCommandPanel();
  appState.sending = true;
  setInputsDisabled(true);
  if (clearInput) els.inputEl.value = '';

  addTextMessage(text, 'sent');
  showTyping();
  try {
    let gotFirst = false;
    await sendMessage(text, (msg) => {
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
    addTextMessage(`[${errorMessage(error)}]`, 'received');
  }
  appState.sending = false;
  setInputsDisabled(false);
  els.inputEl.focus();
}

async function sendFileToApi(file: File, fileType: FileUploadType, caption: string): Promise<void> {
  let gotFirst = false;
  await sendFile(file, fileType, caption, (msg) => {
    if (!gotFirst) {
      hideTyping();
      gotFirst = true;
    }
    renderBotResponse(msg);
  });
  if (!gotFirst) hideTyping();
}

export async function handleSend(): Promise<void> {
  const els = getEls();
  const text = els.inputEl.value.trim();
  const hasFiles = appState.stagedFiles.length > 0;
  if (!text && !hasFiles) return;

  if (!hasFiles) {
    await sendTextMessage(text, { clearInput: true });
    return;
  }

  if (appState.sending) return;

  closeCommandPanel();
  appState.sending = true;
  setInputsDisabled(true);
  els.inputEl.value = '';

  const filesToSend = consumeStagedFiles();

  for (const [i, sf] of filesToSend.entries()) {
    const caption = i === 0 ? text : '';

    switch (sf.type) {
      case 'photo': {
        addPhotoMessage(sf.localUrl, 'sent', caption);
        break;
      }
      case 'voice': {
        addAudioMessage(sf.localUrl, 'sent', caption);
        break;
      }
      case 'video_note': {
        addVideoNoteMessage(sf.localUrl, 'sent', caption);
        break;
      }
      default: {
        addDocumentMessage(sf.file.name, sf.localUrl, 'sent', caption);
      }
    }

    showTyping();
    try {
      await sendFileToApi(sf.file, sf.type, caption);
    } catch (error) {
      hideTyping();
      addTextMessage(`[${errorMessage(error)}]`, 'received');
    }
  }

  appState.sending = false;
  setInputsDisabled(false);
  els.inputEl.focus();
  await refreshBotState();
}
