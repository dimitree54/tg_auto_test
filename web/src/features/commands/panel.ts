import { getState } from '../../api/bot';
import { appState } from '../../state/app';
import type { BotCommandInfo } from '../../types/api';
import { getEls } from '../../ui/dom';

import { commandsState } from './state';

type PanelMode = 'menu' | 'slash';

let panelOpen = false;
let panelMode: PanelMode = 'menu';
let panelItems: BotCommandInfo[] = [];
let selectedIndex = -1;
let onSendCommand: ((text: string) => Promise<void>) | null = null;

export function initCommandsPanel(sendCommand: (text: string) => Promise<void>): void {
  onSendCommand = sendCommand;

  const els = getEls();
  els.menuBtn.addEventListener('click', (e) => {
    e.preventDefault();
    if (appState.sending) return;
    if (!els.menuBtn.classList.contains('visible')) return;
    if (panelOpen && panelMode === 'menu') {
      closeCommandPanel();
      maybeShowSlashSuggestions();
      return;
    }
    openMenuPanel();
  });

  els.inputEl.addEventListener('input', () => {
    maybeShowSlashSuggestions();
  });

  els.inputEl.addEventListener('keydown', (e) => {
    if (!panelOpen) return;

    if (e.key === 'Escape') {
      e.preventDefault();
      closeCommandPanel();
      return;
    }

    if (panelItems.length > 0) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        moveCommandSelection(1);
        return;
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        moveCommandSelection(-1);
        return;
      }
    }

    if (e.key === 'Enter' && activateSelectedCommand()) {
      e.preventDefault();
    }
  });

  document.addEventListener('click', (e) => {
    if (!panelOpen) return;
    const t = e.target;
    if (!(t instanceof Node)) return;
    if (els.commandPanelEl.contains(t)) return;
    if (els.menuBtn.contains(t)) return;
    if (els.inputEl.contains(t)) return;
    closeCommandPanel();
  });
}

export function closeCommandPanel(): void {
  const els = getEls();
  panelOpen = false;
  panelMode = 'menu';
  panelItems = [];
  selectedIndex = -1;
  els.commandPanelEl.classList.remove('visible');
  els.commandPanelEl.innerHTML = '';
}

function openMenuPanel(): void {
  renderCommandPanel('menu', commandsState.botCommands, 'Commands');
}

function maybeShowSlashSuggestions(): void {
  if (panelOpen && panelMode === 'menu') return;

  const query = getSlashQuery();
  if (query === null || commandsState.botCommands.length === 0) {
    if (panelOpen && panelMode === 'slash') closeCommandPanel();
    return;
  }

  const items: BotCommandInfo[] = [];
  for (const cmd of commandsState.botCommands) {
    if (cmd.command && cmd.command.indexOf(query) === 0) items.push(cmd);
  }

  if (items.length === 0) {
    if (panelOpen && panelMode === 'slash') closeCommandPanel();
    return;
  }

  renderCommandPanel('slash', items, query ? `Commands matching "/${query}"` : 'Commands');
}

function getSlashQuery(): string | null {
  const { inputEl } = getEls();
  const text = inputEl.value || '';
  if (!text.startsWith('/')) return null;
  if (/\s/.test(text)) return null;
  return text.slice(1);
}

function renderCommandPanel(mode: PanelMode, items: BotCommandInfo[], title: string): void {
  const els = getEls();

  panelMode = mode;
  panelItems = Array.isArray(items) ? items : [];
  selectedIndex = panelItems.length > 0 ? 0 : -1;
  panelOpen = true;

  els.commandPanelEl.innerHTML = '';
  const card = document.createElement('div');
  card.className = 'cp-card';

  const header = document.createElement('div');
  header.className = 'cp-header';
  header.textContent = title;
  card.appendChild(header);

  if (panelItems.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'cp-empty';
    empty.textContent = 'No commands.';
    card.appendChild(empty);
  } else {
    for (const [i, it] of panelItems.entries()) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = `cp-item${i === selectedIndex ? ' selected' : ''}`;
      btn.dataset.index = String(i);
      btn.addEventListener('click', () => {
        const idx = Number.parseInt(btn.dataset.index || '', 10);
        if (!Number.isFinite(idx)) return;
        selectedIndex = idx;
        updateCommandPanelSelection();
        void activateSelectedCommand();
      });

      const cmdEl = document.createElement('div');
      cmdEl.className = 'cp-cmd';
      cmdEl.textContent = `/${it.command || '?'}`;
      btn.appendChild(cmdEl);

      if (it.description) {
        const descEl = document.createElement('div');
        descEl.className = 'cp-desc';
        descEl.textContent = it.description;
        btn.appendChild(descEl);
      }

      card.appendChild(btn);
    }
  }

  els.commandPanelEl.appendChild(card);
  els.commandPanelEl.classList.add('visible');
}

function updateCommandPanelSelection(): void {
  const els = getEls();
  const btns = els.commandPanelEl.querySelectorAll<HTMLButtonElement>('.cp-item');
  for (const [i, btn] of btns.entries()) {
    if (i === selectedIndex) btn.classList.add('selected');
    else btn.classList.remove('selected');
  }
}

function moveCommandSelection(delta: number): void {
  if (!panelOpen || panelItems.length === 0) return;
  selectedIndex = (selectedIndex + delta) % panelItems.length;
  if (selectedIndex < 0) selectedIndex += panelItems.length;
  updateCommandPanelSelection();
}

function activateSelectedCommand(): boolean {
  if (!panelOpen || selectedIndex < 0 || selectedIndex >= panelItems.length) return false;
  const it = panelItems[selectedIndex];
  const cmd = it.command || '';
  if (!cmd) return false;

  const { inputEl } = getEls();
  if (panelMode === 'slash') {
    inputEl.value = `/${cmd} `;
    closeCommandPanel();
    inputEl.focus();
    return true;
  }

  closeCommandPanel();
  if (onSendCommand) void onSendCommand(`/${cmd}`);
  return true;
}

function updateMenuButtonVisibility(): void {
  const els = getEls();
  const enabled =
    commandsState.menuButtonType === 'commands' && commandsState.botCommands.length > 0;
  if (enabled) {
    els.menuBtn.classList.add('visible');
  } else {
    els.menuBtn.classList.remove('visible');
    if (panelOpen && panelMode === 'menu') closeCommandPanel();
  }
}

export async function refreshBotState(): Promise<void> {
  try {
    const st = await getState();
    commandsState.botCommands = Array.isArray(st.commands) ? st.commands : [];
    commandsState.menuButtonType = st.menu_button_type || 'default';
    updateMenuButtonVisibility();
    if (panelOpen && panelMode === 'menu') {
      openMenuPanel();
    } else if (!panelOpen) {
      maybeShowSlashSuggestions();
    }
  } catch {
    // Ignore state refresh errors in the demo UI.
  }
}

export function resetCommandsState(): void {
  commandsState.botCommands = [];
  commandsState.menuButtonType = 'default';
  updateMenuButtonVisibility();
  closeCommandPanel();
}
