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
  onEvent: (data: T) => void,
): Promise<void> {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw await httpError('POST', path, res);
  await readSSE(res, onEvent);
}

export async function postFormSSE<T>(
  path: string,
  form: FormData,
  onEvent: (data: T) => void,
): Promise<void> {
  const res = await fetch(path, { method: 'POST', body: form });
  if (!res.ok) throw await httpError('POST', path, res);
  await readSSE(res, onEvent);
}

async function readSSE<T>(res: Response, onEvent: (data: T) => void): Promise<void> {
  const reader = res.body?.getReader();
  if (!reader) return;

  const decoder = new TextDecoder();
  let buffer = '';

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const parts = buffer.split('\n\n');
    buffer = parts.pop() ?? '';

    for (const part of parts) {
      const line = part.trim();
      if (!line.startsWith('data: ')) continue;
      const payload = line.slice('data: '.length);
      if (payload === '[DONE]') continue;
      onEvent(JSON.parse(payload) as T);
    }
  }
}
