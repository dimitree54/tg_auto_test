import type { DemoTraceEvent } from '../types/api';

async function readJson<T>(res: Response): Promise<T> {
  const data = (await res.json()) as T;
  return data;
}

async function httpError(method: string, path: string, res: Response): Promise<Error> {
  try {
    const body = (await res.json()) as { detail?: string };
    if (body.detail) {
      return new Error(body.detail);
    }
  } catch {
    // Response body is not JSON — fall through to generic message
  }
  return new Error(`${method} ${path} failed: ${res.status} ${res.statusText}`);
}

export async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(path, { method: 'GET' });
  if (!res.ok) throw await httpError('GET', path, res);
  return await readJson<T>(res);
}

export async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw await httpError('POST', path, res);
  return await readJson<T>(res);
}

export async function postNoBody<T>(path: string): Promise<T> {
  const res = await fetch(path, { method: 'POST' });
  if (!res.ok) throw await httpError('POST', path, res);
  return await readJson<T>(res);
}

export async function postJsonSSE<T>(
  path: string,
  body: unknown,
  callbacks: {
    onMessage: (data: T) => void;
    onTrace: (event: DemoTraceEvent) => void;
  },
  headers: HeadersInit = {},
): Promise<void> {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw await httpError('POST', path, res);
  await readSSE(res, callbacks);
}

export async function postFormSSE<T>(
  path: string,
  form: FormData,
  callbacks: {
    onMessage: (data: T) => void;
    onTrace: (event: DemoTraceEvent) => void;
  },
  headers: HeadersInit = {},
): Promise<void> {
  const res = await fetch(path, { method: 'POST', body: form, headers });
  if (!res.ok) throw await httpError('POST', path, res);
  await readSSE(res, callbacks);
}

async function readSSE<T>(
  res: Response,
  callbacks: {
    onMessage: (data: T) => void;
    onTrace: (event: DemoTraceEvent) => void;
  },
): Promise<void> {
  const reader = res.body?.getReader();
  if (!reader) return;

  const decoder = new TextDecoder();
  let buffer = '';
  let failureDetail = '';

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const parts = buffer.split('\n\n');
    buffer = parts.pop() ?? '';

    for (const part of parts) {
      const lines = part
        .split('\n')
        .map((line) => line.trim())
        .filter(Boolean);
      let eventName = 'message';
      const dataLines: string[] = [];
      for (const line of lines) {
        if (line.startsWith('event: ')) eventName = line.slice('event: '.length);
        if (line.startsWith('data: ')) dataLines.push(line.slice('data: '.length));
      }
      if (dataLines.length === 0) continue;
      const payload = dataLines.join('\n');
      if (payload === '[DONE]') continue;
      if (eventName === 'trace') {
        const event = JSON.parse(payload) as DemoTraceEvent;
        callbacks.onTrace(event);
        if (event.name === 'request_failed') {
          const detail = event.payload.detail;
          failureDetail = typeof detail === 'string' ? detail : 'Demo request failed';
        }
        continue;
      }
      callbacks.onMessage(JSON.parse(payload) as T);
    }
  }
  if (failureDetail) throw new Error(failureDetail);
}
