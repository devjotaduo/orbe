import { getApiUrl } from "../config";
import { buildAuthHeaders } from "../authHeaders";
import type { AguiEvent } from "../types/agui";

/**
 * Split an SSE buffer into parsed JSON events plus the unparsed remainder.
 *
 * Pure + synchronous so it is unit-testable without a real network stream.
 * A complete frame is everything up to a blank line (`\n\n`); the `data: ` line
 * inside it carries one JSON-encoded AG-UI event. A trailing partial frame
 * (no terminating blank line yet) is returned in `rest` to be re-fed next read.
 */
export function parseSseFrames(buffer: string): {
  events: unknown[];
  rest: string;
} {
  const events: unknown[] = [];
  let rest = buffer;
  let idx: number;
  while ((idx = rest.indexOf("\n\n")) !== -1) {
    const frame = rest.slice(0, idx);
    rest = rest.slice(idx + 2);
    const line = frame.split("\n").find((l) => l.startsWith("data: "));
    if (!line) continue;
    const json = line.slice("data: ".length);
    try {
      events.push(JSON.parse(json));
    } catch {
      // Malformed frame: skip it — never throw inside the stream loop.
    }
  }
  return { events, rest };
}

/**
 * POST `body` to `path` and stream the `text/event-stream` response, invoking
 * `onEvent` for each parsed AG-UI event. Resolves when the stream ends.
 *
 * Shared by every discovery streaming endpoint — these are POSTs returning
 * SSE, so we read the `ReadableStream` directly (EventSource only does GET).
 */
async function streamPost(
  path: string,
  body: Record<string, unknown>,
  onEvent: (ev: AguiEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const resp = await fetch(getApiUrl(path), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(),
    },
    body: JSON.stringify(body),
    signal,
  });
  if (!resp.ok) {
    throw new Error(`discovery stream failed: ${resp.status}`);
  }
  if (!resp.body) {
    throw new Error("discovery stream: no response body");
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  try {
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const { events, rest } = parseSseFrames(buffer);
      buffer = rest;
      for (const ev of events) onEvent(ev as AguiEvent);
    }
    // Flush any trailing multibyte sequence the streaming decoder held back,
    // then parse a final frame that may not end in a blank line.
    buffer += decoder.decode();
    const tail = parseSseFrames(buffer);
    for (const ev of tail.events) onEvent(ev as AguiEvent);
  } finally {
    reader.releaseLock();
  }
}

export const discoveryApi = {
  /**
   * Advance the discovery interview by one turn, invoking `onEvent` for each
   * AG-UI event as it streams in. Resolves when the turn's stream ends.
   */
  async streamTurn(
    sessionId: string,
    message: string | null,
    onEvent: (ev: AguiEvent) => void,
    signal?: AbortSignal,
  ): Promise<void> {
    return streamPost(
      "/discovery/stream",
      { session_id: sessionId, message },
      onEvent,
      signal,
    );
  },

  /**
   * Dispatch a surface action (e.g. `approve_team`) with the client-edited
   * data model. Streams the backend's AG-UI confirmation/error events.
   */
  async action(
    sessionId: string,
    name: string,
    data: Record<string, unknown>,
    onEvent: (ev: AguiEvent) => void,
    signal?: AbortSignal,
  ): Promise<void> {
    return streamPost(
      "/discovery/action",
      { session_id: sessionId, action: name, data },
      onEvent,
      signal,
    );
  },
};
