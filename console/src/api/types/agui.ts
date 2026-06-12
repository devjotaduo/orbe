/**
 * AG-UI event types (TypeScript mirror of the backend Pydantic schemas).
 *
 * Each event has a SCREAMING_SNAKE `type` discriminator and camelCase wire
 * fields, matching `src/qwenpaw/agui/events.py`. The discovery SSE stream
 * (`POST /discovery/stream`) emits exactly these.
 */
export type AguiEvent =
  | { type: "RUN_STARTED"; threadId: string; runId: string }
  | { type: "RUN_FINISHED"; threadId: string; runId: string }
  | { type: "RUN_ERROR"; message: string; code?: string }
  | { type: "TEXT_MESSAGE_START"; messageId: string; role?: string }
  | { type: "TEXT_MESSAGE_CONTENT"; messageId: string; delta: string }
  | { type: "TEXT_MESSAGE_END"; messageId: string }
  | { type: "STATE_SNAPSHOT"; snapshot: Record<string, unknown> }
  | { type: "STATE_DELTA"; delta: Array<Record<string, unknown>> }
  | { type: "CUSTOM"; name: string; value: Record<string, unknown> };
