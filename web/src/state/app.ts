import type { FileUploadType } from '../types/api';

export interface StagedFile {
  file: File;
  type: FileUploadType;
  localUrl: string;
}

export const appState = {
  sending: false,
  stagedFiles: [] as StagedFile[],
};
