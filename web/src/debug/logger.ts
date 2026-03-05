import type { DemoTraceEvent, MessageResponse } from '../types/api';

export interface UiTrace {
  action: string;
  id: string;
}

let traceCounter = 0;
const openGroups = new Set<string>();

function nextTraceId(action: string): string {
  traceCounter += 1;
  return `${action}-${traceCounter}`;
}

function tracePrefix(traceId: string): string {
  return `[demo ${traceId}]`;
}

function traceEvent(
  traceId: string,
  name: string,
  payload: Record<string, unknown> = {},
): DemoTraceEvent {
  return {
    trace_id: traceId,
    scope: 'ui',
    name,
    ts: new Date().toISOString(),
    payload,
  };
}

function groupLabel(trace: UiTrace): string {
  return `${tracePrefix(trace.id)} ${trace.action}`;
}

function ensureGroup(trace: UiTrace): void {
  if (openGroups.has(trace.id)) return;
  openGroups.add(trace.id);
  console.groupCollapsed(groupLabel(trace));
}

function closeGroup(traceId: string): void {
  if (!openGroups.has(traceId)) return;
  openGroups.delete(traceId);
  console.groupEnd();
}

export function startUiTrace(
  action: string,
  payload: Record<string, unknown> = {},
): UiTrace {
  const trace = { action, id: nextTraceId(action) };
  ensureGroup(trace);
  console.debug(tracePrefix(trace.id), traceEvent(trace.id, action, payload));
  return trace;
}

export function logUiEvent(
  name: string,
  payload: Record<string, unknown> = {},
  traceId?: string,
): void {
  if (traceId) {
    console.debug(tracePrefix(traceId), traceEvent(traceId, name, payload));
    return;
  }
  console.debug('[demo]', {
    ...traceEvent('standalone', name, payload),
    trace_id: 'standalone',
  });
}

export function logTraceEvent(event: DemoTraceEvent): void {
  console.debug(tracePrefix(event.trace_id), event);
}

export function logMessageRendered(traceId: string | undefined, message: MessageResponse): void {
  const payload = {
    is_edit: Boolean(message.is_edit),
    message_id: message.message_id,
    message_type: message.type,
  };
  if (traceId) {
    console.info(tracePrefix(traceId), traceEvent(traceId, 'message_rendered', payload));
    return;
  }
  console.info('[demo]', traceEvent('standalone', 'message_rendered', payload));
}

export function finishUiTrace(trace: UiTrace, payload: Record<string, unknown> = {}): void {
  console.debug(tracePrefix(trace.id), traceEvent(trace.id, 'request_completed', payload));
  closeGroup(trace.id);
}

export function failUiTrace(
  trace: UiTrace,
  error: unknown,
  payload: Record<string, unknown> = {},
): void {
  console.error(tracePrefix(trace.id), traceEvent(trace.id, 'ui_error', {
    ...payload,
    message: error instanceof Error ? error.message : String(error),
  }));
  closeGroup(trace.id);
}
