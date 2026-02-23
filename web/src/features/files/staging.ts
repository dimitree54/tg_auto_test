import { appState, type StagedFile } from '../../state/app';
import type { FileUploadType } from '../../types/api';
import { getEls } from '../../ui/dom';

function detectFileType(file: File): FileUploadType {
  const t = file.type || '';
  if (t.startsWith('image/')) return 'photo';
  if (t.startsWith('audio/')) return 'voice';
  if (t.startsWith('video/')) return 'video_note';
  return 'document';
}

function stageFile(file: File): void {
  const localUrl = URL.createObjectURL(file);
  appState.stagedFiles.push({ file, type: detectFileType(file), localUrl });
  renderStagedFiles();
}

function unstageFile(index: number): void {
  const sf = appState.stagedFiles[index];
  if (!sf) return;
  URL.revokeObjectURL(sf.localUrl);
  appState.stagedFiles.splice(index, 1);
  renderStagedFiles();
}

export function clearStaged(): void {
  for (const sf of appState.stagedFiles) URL.revokeObjectURL(sf.localUrl);
  appState.stagedFiles = [];
  renderStagedFiles();
}

export function consumeStagedFiles(): StagedFile[] {
  const files = [...appState.stagedFiles];
  // Keep object URLs alive because they are used for sent previews.
  appState.stagedFiles = [];
  renderStagedFiles();
  return files;
}

function renderStagedFiles(): void {
  const els = getEls();
  els.stagedFilesEl.innerHTML = '';
  if (appState.stagedFiles.length === 0) {
    els.stagedFilesEl.classList.remove('visible');
    return;
  }

  els.stagedFilesEl.classList.add('visible');
  for (let i = 0; i < appState.stagedFiles.length; i++) {
    const sf = appState.stagedFiles[i];
    const item = document.createElement('div');
    item.className = 'staged-item';

    if (sf.type === 'photo') {
      const img = document.createElement('img');
      img.src = sf.localUrl;
      img.alt = 'Preview';
      item.appendChild(img);
    } else {
      const icon = document.createElement('span');
      icon.className = 'staged-icon';
      const iconMap: Record<string, string> = {
        voice: '&#127908;',
        video_note: '&#127909;',
      };
      icon.innerHTML = iconMap[sf.type] ?? '&#128196;';
      item.appendChild(icon);
    }

    const name = document.createElement('span');
    name.className = 'staged-name';
    name.textContent = sf.file.name;
    item.appendChild(name);

    const removeBtn = document.createElement('button');
    removeBtn.className = 'staged-remove';
    removeBtn.innerHTML = '&times;';
    removeBtn.dataset.index = String(i);
    removeBtn.addEventListener('click', () => {
      const idx = Number.parseInt(removeBtn.dataset.index || '', 10);
      if (!Number.isFinite(idx)) return;
      unstageFile(idx);
    });
    item.appendChild(removeBtn);

    els.stagedFilesEl.appendChild(item);
  }
}

export function initFileStaging(): void {
  const els = getEls();

  els.attachBtn.addEventListener('click', () => {
    if (!appState.sending) els.fileInput.click();
  });

  els.fileInput.addEventListener('change', () => {
    const files = els.fileInput.files;
    if (files && files.length > 0) {
      for (let i = 0; i < files.length; i++) stageFile(files[i]);
    }
    els.fileInput.value = '';
    els.inputEl.focus();
  });

  els.chatContainer.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.stopPropagation();
  });

  els.chatContainer.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      for (let i = 0; i < files.length; i++) stageFile(files[i]);
    }
  });
}
