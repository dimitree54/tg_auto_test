import type { BotStateResponse, FileUploadType, MessageResponse } from '../types/api';

import { getJson, postForm, postJson, postNoBody } from './http';

export async function sendMessage(text: string): Promise<MessageResponse> {
  return await postJson<MessageResponse>('/api/message', { text });
}

export async function sendFile(
  file: File,
  kind: FileUploadType,
  caption: string,
): Promise<MessageResponse> {
  const form = new FormData();
  form.append('file', file);
  if (caption) form.append('caption', caption);
  return await postForm<MessageResponse>(`/api/${kind}`, form);
}

export async function pressCallback(messageId: number, data: string): Promise<MessageResponse> {
  return await postJson<MessageResponse>('/api/callback', { message_id: messageId, data });
}

export async function payInvoice(messageId: number): Promise<MessageResponse> {
  return await postJson<MessageResponse>('/api/invoice/pay', { message_id: messageId });
}

export async function resetConversation(): Promise<{ status: string }> {
  return await postNoBody<{ status: string }>('/api/reset');
}

export async function getState(): Promise<BotStateResponse> {
  return await getJson<BotStateResponse>('/api/state');
}

export async function votePoll(messageId: number, optionIds: number[]): Promise<MessageResponse> {
  return await postJson<MessageResponse>('/api/poll/vote', { message_id: messageId, option_ids: optionIds });
}
