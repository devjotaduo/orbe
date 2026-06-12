import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { parseSseFrames, discoveryApi } from "./discovery";
import type { AguiEvent } from "../types/agui";

vi.mock("../config", () => ({
  getApiUrl: (path: string) => `/api${path}`,
}));
vi.mock("../authHeaders", () => ({
  buildAuthHeaders: () => ({ Authorization: "Bearer test" }),
}));

/**
 * Build a fetch Response whose body is a ReadableStream that emits the given
 * UTF-8 chunks in order. Each `chunk` is delivered as one `reader.read()`
 * resolution, letting us deliberately split an SSE frame across reads.
 */
function streamResponse(chunks: string[]): Response {
  const enc = new TextEncoder();
  let i = 0;
  const body = new ReadableStream<Uint8Array>({
    pull(controller) {
      if (i < chunks.length) {
        controller.enqueue(enc.encode(chunks[i++]));
      } else {
        controller.close();
      }
    },
  });
  return { ok: true, status: 200, body } as unknown as Response;
}

describe("parseSseFrames", () => {
  it("extracts JSON objects from complete data frames", () => {
    const buf =
      'data: {"type":"RUN_STARTED","threadId":"t","runId":"r"}\n\n' +
      'data: {"type":"TEXT_MESSAGE_CONTENT","messageId":"m","delta":"oi"}\n\n';
    const { events, rest } = parseSseFrames(buf);
    expect(events.map((e) => (e as { type: string }).type)).toEqual([
      "RUN_STARTED",
      "TEXT_MESSAGE_CONTENT",
    ]);
    expect(rest).toBe("");
  });

  it("keeps an incomplete trailing frame in rest", () => {
    const buf = 'data: {"type":"RUN_FINISHED"}\n\ndata: {"type":"CUST';
    const { events, rest } = parseSseFrames(buf);
    expect(events).toHaveLength(1);
    expect(rest).toBe('data: {"type":"CUST');
  });
});

describe("discoveryApi.streamTurn", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.clearAllMocks();
  });

  it("POSTs to /api/discovery/stream with session, message and auth", async () => {
    (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(
      streamResponse([
        'data: {"type":"RUN_FINISHED","threadId":"t","runId":"r"}\n\n',
      ]),
    );

    await discoveryApi.streamTurn("sess-1", "hello", () => {});

    expect(fetch).toHaveBeenCalledTimes(1);
    const [url, init] = (fetch as unknown as ReturnType<typeof vi.fn>).mock
      .calls[0];
    expect(url).toBe("/api/discovery/stream");
    expect(init.method).toBe("POST");
    expect(init.headers).toMatchObject({
      "Content-Type": "application/json",
      Authorization: "Bearer test",
    });
    expect(JSON.parse(init.body)).toEqual({
      session_id: "sess-1",
      message: "hello",
    });
  });

  it("emits correctly-typed events in order across a frame split between reads", async () => {
    // The TEXT_MESSAGE_CONTENT frame is deliberately cut mid-JSON so the buffer
    // carry-over (rest) path is exercised end-to-end, not just in the pure unit.
    (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(
      streamResponse([
        'data: {"type":"RUN_STARTED","threadId":"t","runId":"r"}\n\ndata: {"type":"TEXT_MESSAGE_CON',
        'TENT","messageId":"m","delta":"hi"}\n\ndata: {"type":"RUN_FINISHED","threadId":"t","runId":"r"}\n\n',
      ]),
    );

    const seen: AguiEvent[] = [];
    await discoveryApi.streamTurn("sess-1", null, (ev) => seen.push(ev));

    expect(seen.map((e) => e.type)).toEqual([
      "RUN_STARTED",
      "TEXT_MESSAGE_CONTENT",
      "RUN_FINISHED",
    ]);
    const content = seen[1];
    expect(content.type === "TEXT_MESSAGE_CONTENT" && content.delta).toBe("hi");
  });

  it("forwards an AbortSignal to fetch when provided", async () => {
    // streamTurn takes (sessionId, message, onEvent, signal?) and passes the
    // signal into fetch so the caller can cancel an in-flight turn (unmount).
    (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(
      streamResponse([
        'data: {"type":"RUN_FINISHED","threadId":"t","runId":"r"}\n\n',
      ]),
    );

    const controller = new AbortController();
    await discoveryApi.streamTurn("sess-1", null, () => {}, controller.signal);

    expect(discoveryApi.streamTurn.length).toBe(4);
    const [, init] = (fetch as unknown as ReturnType<typeof vi.fn>).mock
      .calls[0];
    expect(init.signal).toBe(controller.signal);
  });

  it("throws when the response is not ok", async () => {
    (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: false,
      status: 503,
      body: null,
    } as unknown as Response);

    await expect(
      discoveryApi.streamTurn("sess-1", null, () => {}),
    ).rejects.toThrow(/503/);
  });

  it("action POSTs to /api/discovery/action and streams events", async () => {
    (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(
      streamResponse([
        'data: {"type":"RUN_FINISHED","threadId":"t","runId":"r"}\n\n',
      ]),
    );

    const seen: string[] = [];
    await discoveryApi.action("s1", "approve_team", { a: 1 }, (ev) =>
      seen.push(ev.type),
    );

    const [url, init] = (fetch as unknown as ReturnType<typeof vi.fn>).mock
      .calls[0];
    expect(url).toBe("/api/discovery/action");
    expect(init.method).toBe("POST");
    expect(init.headers).toMatchObject({
      "Content-Type": "application/json",
      Authorization: "Bearer test",
    });
    expect(JSON.parse(init.body)).toEqual({
      session_id: "s1",
      action: "approve_team",
      data: { a: 1 },
    });
    expect(seen).toEqual(["RUN_FINISHED"]);
  });

  it("action forwards an AbortSignal to fetch when provided", async () => {
    (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(
      streamResponse([
        'data: {"type":"RUN_FINISHED","threadId":"t","runId":"r"}\n\n',
      ]),
    );

    const controller = new AbortController();
    await discoveryApi.action(
      "s1",
      "approve_team",
      {},
      () => {},
      controller.signal,
    );

    const [, init] = (fetch as unknown as ReturnType<typeof vi.fn>).mock
      .calls[0];
    expect(init.signal).toBe(controller.signal);
  });

  it("decodes a multi-byte UTF-8 character split across two reads", async () => {
    // "é" (U+00E9) is two bytes in UTF-8 (0xC3 0xA9); split them across reads
    // to prove the streaming TextDecoder ({ stream: true }) reassembles it.
    const enc = new TextEncoder();
    const full = enc.encode(
      'data: {"type":"TEXT_MESSAGE_CONTENT","messageId":"m","delta":"é"}\n\n',
    );
    // Find a safe split index inside the multi-byte char's bytes.
    const splitAt = full.indexOf(0xc3) + 1;
    let i = 0;
    const parts = [full.slice(0, splitAt), full.slice(splitAt)];
    const body = new ReadableStream<Uint8Array>({
      pull(controller) {
        if (i < parts.length) controller.enqueue(parts[i++]);
        else controller.close();
      },
    });
    (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      status: 200,
      body,
    } as unknown as Response);

    const seen: AguiEvent[] = [];
    await discoveryApi.streamTurn("sess-1", null, (ev) => seen.push(ev));

    const ev = seen[0];
    expect(ev.type === "TEXT_MESSAGE_CONTENT" && ev.delta).toBe("é");
  });
});
