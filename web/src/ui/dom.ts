interface DemoEls {
  messagesEl: HTMLElement;
  inputEl: HTMLInputElement;
  sendBtn: HTMLButtonElement;
  resetBtn: HTMLButtonElement;
  typingEl: HTMLElement;
  attachBtn: HTMLButtonElement;
  fileInput: HTMLInputElement;
  stagedFilesEl: HTMLElement;
  replyKeyboardEl: HTMLElement;
  menuBtn: HTMLButtonElement;
  commandPanelEl: HTMLElement;
  chatContainer: HTMLElement;
}

let cachedEls: DemoEls | null = null;

function requireEl<T extends HTMLElement>(id: string): T {
  const el = document.getElementById(id);
  if (!el) throw new Error(`Missing element: #${id}`);
  return el as T;
}

export function getEls(): DemoEls {
  if (cachedEls) return cachedEls;

  const chatContainer = document.querySelector('.chat-container');
  if (!chatContainer) throw new Error('Missing element: .chat-container');

  cachedEls = {
    messagesEl: requireEl<HTMLElement>('messages'),
    inputEl: requireEl<HTMLInputElement>('msgInput'),
    sendBtn: requireEl<HTMLButtonElement>('sendBtn'),
    resetBtn: requireEl<HTMLButtonElement>('resetBtn'),
    typingEl: requireEl<HTMLElement>('typing'),
    attachBtn: requireEl<HTMLButtonElement>('attachBtn'),
    fileInput: requireEl<HTMLInputElement>('fileInput'),
    stagedFilesEl: requireEl<HTMLElement>('stagedFiles'),
    replyKeyboardEl: requireEl<HTMLElement>('replyKeyboard'),
    menuBtn: requireEl<HTMLButtonElement>('menuBtn'),
    commandPanelEl: requireEl<HTMLElement>('commandPanel'),
    chatContainer: chatContainer as HTMLElement,
  };
  return cachedEls;
}

export function setInputsDisabled(disabled: boolean): void {
  const els = getEls();
  els.sendBtn.disabled = disabled;
  els.attachBtn.disabled = disabled;
}
