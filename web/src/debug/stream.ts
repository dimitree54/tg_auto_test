import type { DemoTraceEvent, MessageResponse } from '../types/api';

import { logMessageRendered, logTraceEvent } from './logger';

interface StreamCallbacks {
  onMessage: (message: MessageResponse) => void;
  onTrace: (event: DemoTraceEvent) => void;
}

export function createStreamCallbacks(
  traceId: string,
  onMessage: (message: MessageResponse) => void,
): StreamCallbacks {
  return {
    onMessage(message) {
      onMessage(message);
      logMessageRendered(traceId, message);
    },
    onTrace(event) {
      logTraceEvent(event);
    },
  };
}
