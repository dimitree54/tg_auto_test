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

export async function postForm<T>(path: string, form: FormData): Promise<T> {
  const res = await fetch(path, { method: 'POST', body: form });
  if (!res.ok) throw await httpError('POST', path, res);
  return await readJson<T>(res);
}
