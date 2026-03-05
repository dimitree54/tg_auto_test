import type { BotStateResponse, FileUploadType, MessageResponse } from '../types/api';

import { getJson, postFormSSE, postJson, postJsonSSE, postNoBody } from './http';

export async function sendMessage(
  text: string,
  onEvent: (msg: MessageResponse) => void,
): Promise<void> {
  await postJsonSSE<MessageResponse>('/api/message', { text }, onEvent);
}

export async function sendFile(
  file: File,
  kind: FileUploadType,
  caption: string,
  onEvent: (msg: MessageResponse) => void,
): Promise<void> {
  const form = new FormData();
  form.append('file', file);
  if (caption) form.append('caption', caption);
  await postFormSSE<MessageResponse>(`/api/${kind}`, form, onEvent);
}

export async function pressCallback(messageId: number, data: string): Promise<MessageResponse> {
  return await postJson<MessageResponse>('/api/callback', { message_id: messageId, data });
}

export async function payInvoice(
  messageId: number,
  onEvent: (msg: MessageResponse) => void,
): Promise<void> {
  await postJsonSSE<MessageResponse>('/api/invoice/pay', { message_id: messageId }, onEvent);
}

export async function resetConversation(): Promise<{ status: string }> {
  return await postNoBody<{ status: string }>('/api/reset');
}

export async function getState(): Promise<BotStateResponse> {
  return await getJson<BotStateResponse>('/api/state');
}

export async function votePoll(
  messageId: number,
  optionIds: number[],
  onEvent: (msg: MessageResponse) => void,
): Promise<void> {
  await postJsonSSE<MessageResponse>(
    '/api/poll/vote',
    { message_id: messageId, option_ids: optionIds },
    onEvent,
  );
}
