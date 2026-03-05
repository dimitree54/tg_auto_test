import type { BotStateResponse, DemoTraceEvent, FileUploadType, MessageResponse } from '../types/api';

import { getJson, postFormSSE, postJsonSSE, postNoBody } from './http';

interface TraceCallbacks {
  onMessage: (msg: MessageResponse) => void;
  onTrace: (event: DemoTraceEvent) => void;
}

export async function sendMessage(
  text: string,
  traceId: string,
  callbacks: TraceCallbacks,
): Promise<void> {
  await postJsonSSE<MessageResponse>('/api/message', { text }, callbacks, { 'X-Demo-Trace-Id': traceId });
}

export async function sendFile(
  file: File,
  kind: FileUploadType,
  caption: string,
  traceId: string,
  callbacks: TraceCallbacks,
): Promise<void> {
  const form = new FormData();
  form.append('file', file);
  if (caption) form.append('caption', caption);
  await postFormSSE<MessageResponse>(`/api/${kind}`, form, callbacks, { 'X-Demo-Trace-Id': traceId });
}

export async function pressCallback(
  messageId: number,
  data: string,
  traceId: string,
  callbacks: TraceCallbacks,
): Promise<void> {
  await postJsonSSE<MessageResponse>(
    '/api/callback',
    { message_id: messageId, data },
    callbacks,
    { 'X-Demo-Trace-Id': traceId },
  );
}

export async function payInvoice(
  messageId: number,
  traceId: string,
  callbacks: TraceCallbacks,
): Promise<void> {
  await postJsonSSE<MessageResponse>(
    '/api/invoice/pay',
    { message_id: messageId },
    callbacks,
    { 'X-Demo-Trace-Id': traceId },
  );
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
  traceId: string,
  callbacks: TraceCallbacks,
): Promise<void> {
  await postJsonSSE<MessageResponse>(
    '/api/poll/vote',
    { message_id: messageId, option_ids: optionIds },
    callbacks,
    { 'X-Demo-Trace-Id': traceId },
  );
}
