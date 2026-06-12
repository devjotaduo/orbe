/**
 * a2uiChatToolRender.test.tsx — covers the a2ui-chat plugin bundle's
 * `A2uiToolRender` (Phase B interactivity), flagged as MISSING TESTS:
 *
 *  - editable: wires `onDataChange` + `onAction`, and onAction POSTs to
 *    host.fetch("/a2ui/action", ...) with {session_id, action, data, params}.
 *  - read-only (default / unset interactivity): renders statically with
 *    NO onDataChange / onAction handlers.
 *  - safe fallback when host.fetch is missing on the action callback.
 *  - fetchInteractivity falls back to "read-only" on non-ok response,
 *    a thrown fetch, and a missing host.fetch.
 *
 * The plugin file lives outside console/src; it calls install() on import
 * and registers its renderer through window.QwenPaw.registerToolRender,
 * pulling React/A2uiRenderer/applyA2uiMessage/emptySurface from the host.
 * We stub the host, import the bundle, capture the registered renderer,
 * and drive it with @testing-library/react.
 */
import { describe, it, expect, beforeEach, vi } from "vitest";
import React from "react";
import { render, waitFor, act } from "@testing-library/react";

// Vite resolves a *literal* dynamic-import string relative to this file;
// a variable would be resolved against the project root, so import inline.
const importBundle = () =>
  import("../../../plugins/bundle/a2ui-chat/ui/src/index.tsx");

type AnyRec = Record<string, unknown>;
type ToolRender = (props: { data: AnyRec }) => React.ReactNode;

// Captures the props the host A2uiRenderer is invoked with so each test
// can assert what the bundle wired up.
let lastRendererProps: AnyRec | null = null;

function MockRenderer(props: AnyRec) {
  lastRendererProps = props;
  return React.createElement("div", { "data-testid": "a2ui-rendered" }, "ok");
}

/** Minimal surface reducer doubles — enough for parseSurface to succeed. */
function emptySurface(id: string): AnyRec {
  return { surfaceId: id, root: "", components: {}, data: {} };
}
function applyA2uiMessage(surf: AnyRec, msg: AnyRec): AnyRec {
  const next = { ...surf };
  if (msg.messageType === "createSurface") {
    next.root = msg.root;
  } else if (msg.messageType === "updateComponents") {
    const comps: AnyRec = { ...(next.components as AnyRec) };
    for (const c of (msg.components as AnyRec[]) ?? []) {
      comps[c.id as string] = c;
    }
    next.components = comps;
  } else if (msg.messageType === "updateDataModel") {
    next.data = { ...((next.data as AnyRec) ?? {}), ...(msg.data as AnyRec) };
  }
  return next;
}

const SURFACE_MSGS = [
  { messageType: "createSurface", surfaceId: "s", root: "root" },
  {
    messageType: "updateComponents",
    surfaceId: "s",
    components: [
      { id: "root", type: "Column", properties: {}, children: [] },
    ],
  },
  { messageType: "updateDataModel", surfaceId: "s", data: { name: "Ada" } },
];

/** The chat `data` prop the tool renderer receives (output under content[1]). */
function chatData(): AnyRec {
  return {
    content: [
      { type: "tool_use", data: {} },
      { type: "tool_result", data: { output: { surface: SURFACE_MSGS } } },
    ],
  };
}

/** Like chatData() but with a custom seed-data `name`, fresh object each call. */
function chatDataNamed(name: string): AnyRec {
  return {
    content: [
      { type: "tool_use", data: {} },
      {
        type: "tool_result",
        data: {
          output: {
            surface: [
              { messageType: "createSurface", surfaceId: "s", root: "root" },
              {
                messageType: "updateComponents",
                surfaceId: "s",
                components: [
                  { id: "root", type: "Column", properties: {}, children: [] },
                ],
              },
              { messageType: "updateDataModel", surfaceId: "s", data: { name } },
            ],
          },
        },
      },
    ],
  };
}

interface HostOverrides {
  fetch?: unknown;
  getCurrentSessionId?: unknown;
}

/** Install window.QwenPaw with a capturing registerToolRender + host. */
function installHost(over: HostOverrides = {}): {
  host: AnyRec;
  getRenderer: () => ToolRender;
} {
  let captured: ToolRender | null = null;
  const host: AnyRec = {
    React,
    A2uiRenderer: MockRenderer,
    applyA2uiMessage,
    emptySurface,
    ...over,
  };
  (window as unknown as AnyRec).QwenPaw = {
    host,
    registerToolRender: (_id: string, renderers: AnyRec) => {
      captured = renderers.render_ui as ToolRender;
    },
  };
  return {
    host,
    getRenderer: () => {
      if (!captured) throw new Error("renderer not registered");
      return captured;
    },
  };
}

/** Fresh import of the bundle (it install()s on load). */
async function loadBundle(over: HostOverrides = {}): Promise<ToolRender> {
  vi.resetModules();
  const { getRenderer } = installHost(over);
  await importBundle();
  return getRenderer();
}

beforeEach(() => {
  lastRendererProps = null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (window as any).QwenPaw = undefined;
});

describe("A2uiToolRender — read-only (default)", () => {
  it("renders statically with no onDataChange / onAction when fetch missing", async () => {
    // No host.fetch => fetchInteractivity short-circuits to read-only.
    const Renderer = await loadBundle();
    render(React.createElement(Renderer, { data: chatData() }));

    await waitFor(() => expect(lastRendererProps).not.toBeNull());
    expect(lastRendererProps!.surface).toBeTruthy();
    expect(lastRendererProps!.onDataChange).toBeUndefined();
    expect(lastRendererProps!.onAction).toBeUndefined();
  });

  it("stays read-only when config endpoint returns non-ok", async () => {
    const fetchMock = vi.fn(async () => ({ ok: false }) as Response);
    const Renderer = await loadBundle({ fetch: fetchMock });
    render(React.createElement(Renderer, { data: chatData() }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
    await waitFor(() => expect(lastRendererProps).not.toBeNull());
    expect(lastRendererProps!.onAction).toBeUndefined();
  });

  it("stays read-only when config fetch throws", async () => {
    const fetchMock = vi.fn(async () => {
      throw new Error("network down");
    });
    const Renderer = await loadBundle({ fetch: fetchMock });
    render(React.createElement(Renderer, { data: chatData() }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
    await waitFor(() => expect(lastRendererProps).not.toBeNull());
    expect(lastRendererProps!.onAction).toBeUndefined();
  });

  it("stays read-only when interactivity value is not 'editable'", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({ interactivity: "read-only" }),
    }));
    const Renderer = await loadBundle({ fetch: fetchMock });
    render(React.createElement(Renderer, { data: chatData() }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
    await waitFor(() => expect(lastRendererProps).not.toBeNull());
    expect(lastRendererProps!.onAction).toBeUndefined();
    expect(lastRendererProps!.onDataChange).toBeUndefined();
  });
});

describe("A2uiToolRender — editable", () => {
  async function renderEditable(over: HostOverrides = {}) {
    const fetchMock =
      (over.fetch as ReturnType<typeof vi.fn>) ??
      vi.fn(async (p: string) => {
        if (p === "/tools/render_ui/config") {
          return {
            ok: true,
            json: async () => ({ interactivity: "editable" }),
          } as unknown as Response;
        }
        return { ok: true, json: async () => ({}) } as unknown as Response;
      });
    const Renderer = await loadBundle({
      getCurrentSessionId: () => "sess-42",
      ...over,
      fetch: fetchMock,
    });
    render(React.createElement(Renderer, { data: chatData() }));
    await waitFor(() =>
      expect(lastRendererProps?.onAction).toBeInstanceOf(Function),
    );
    return { fetchMock };
  }

  it("wires onDataChange + onAction and seeds data from the surface", async () => {
    await renderEditable();
    expect(lastRendererProps!.onDataChange).toBeInstanceOf(Function);
    expect(lastRendererProps!.onAction).toBeInstanceOf(Function);
    // data model seeded from the surface's updateDataModel.
    expect(lastRendererProps!.data).toEqual({ name: "Ada" });
  });

  it("onAction POSTs to /a2ui/action with {session_id, action, data, params}", async () => {
    const { fetchMock } = await renderEditable();
    const onAction = lastRendererProps!.onAction as (
      n: string,
      p?: AnyRec,
    ) => Promise<void>;

    await act(async () => {
      await onAction("submit", { extra: 1 });
    });

    const calls = fetchMock.mock.calls as unknown as unknown[][];
    const call = calls.find((c) => c[0] === "/a2ui/action");
    expect(call).toBeTruthy();
    const init = call![1] as AnyRec;
    expect(init.method).toBe("POST");
    expect((init.headers as AnyRec)["Content-Type"]).toBe("application/json");
    const body = JSON.parse(init.body as string);
    expect(body).toEqual({
      session_id: "sess-42",
      action: "submit",
      data: { name: "Ada" },
      params: { extra: 1 },
    });
  });

  it("onAction defaults session_id to 'chat' when getCurrentSessionId absent", async () => {
    const fetchMock = vi.fn(async (p: string) => {
      if (p === "/tools/render_ui/config") {
        return {
          ok: true,
          json: async () => ({ interactivity: "editable" }),
        } as unknown as Response;
      }
      return { ok: true, json: async () => ({}) } as unknown as Response;
    });
    // No getCurrentSessionId on the host.
    const Renderer = await loadBundle({ fetch: fetchMock });
    render(React.createElement(Renderer, { data: chatData() }));
    await waitFor(() =>
      expect(lastRendererProps?.onAction).toBeInstanceOf(Function),
    );

    const onAction = lastRendererProps!.onAction as (
      n: string,
    ) => Promise<void>;
    await act(async () => {
      await onAction("ping");
    });

    const calls = fetchMock.mock.calls as unknown as unknown[][];
    const call = calls.find((c) => c[0] === "/a2ui/action");
    const body = JSON.parse((call![1] as AnyRec).body as string);
    expect(body.session_id).toBe("chat");
  });

  it("onAction swallows a thrown fetch (best-effort, surface stays usable)", async () => {
    let configResolved = false;
    const fetchMock = vi.fn(async (p: string) => {
      if (p === "/tools/render_ui/config") {
        configResolved = true;
        return {
          ok: true,
          json: async () => ({ interactivity: "editable" }),
        } as unknown as Response;
      }
      throw new Error("action endpoint down");
    });
    const Renderer = await loadBundle({ fetch: fetchMock });
    render(React.createElement(Renderer, { data: chatData() }));
    await waitFor(() => expect(configResolved).toBe(true));
    await waitFor(() =>
      expect(lastRendererProps?.onAction).toBeInstanceOf(Function),
    );

    const onAction = lastRendererProps!.onAction as (
      n: string,
    ) => Promise<void>;
    // Must not reject even though the POST throws.
    await act(async () => {
      await expect(onAction("submit")).resolves.toBeUndefined();
    });
  });
});

describe("A2uiToolRender — fallbacks", () => {
  it("shows an error fallback when the surface output is unparseable", async () => {
    const Renderer = await loadBundle();
    const badData: AnyRec = {
      content: [
        { type: "tool_use", data: {} },
        { type: "tool_result", data: { output: "not-json{" } },
      ],
    };
    const { container } = render(
      React.createElement(Renderer, { data: badData }),
    );
    await waitFor(() =>
      expect(container.textContent).toContain("A2UI: surface inválida"),
    );
    expect(lastRendererProps).toBeNull();
  });
});

describe("A2uiToolRender — hooks stability & re-seed", () => {
  const unparseable: AnyRec = {
    content: [
      { type: "tool_use", data: {} },
      { type: "tool_result", data: { output: "not-json{" } },
    ],
  };

  it("survives a surface null -> real transition on the same instance", async () => {
    // A conditional early-return before the hooks would make React throw
    // "rendered more hooks than during the previous render" here.
    const Renderer = await loadBundle();
    const { rerender, container } = render(
      React.createElement(Renderer, { data: unparseable }),
    );
    await waitFor(() =>
      expect(container.textContent).toContain("A2UI: surface inválida"),
    );
    expect(lastRendererProps).toBeNull();

    rerender(React.createElement(Renderer, { data: chatData() }));
    await waitFor(() => expect(lastRendererProps).not.toBeNull());
    expect(lastRendererProps!.surface).toBeTruthy();
  });

  it("re-seeds the editable data model when a new surface arrives in-place", async () => {
    const fetchMock = vi.fn(async (p: string) => {
      if (p === "/tools/render_ui/config") {
        return {
          ok: true,
          json: async () => ({ interactivity: "editable" }),
        } as unknown as Response;
      }
      return { ok: true, json: async () => ({}) } as unknown as Response;
    });
    const Renderer = await loadBundle({ fetch: fetchMock });
    const { rerender } = render(
      React.createElement(Renderer, { data: chatDataNamed("Ada") }),
    );
    await waitFor(() =>
      expect(lastRendererProps?.onAction).toBeInstanceOf(Function),
    );
    expect(lastRendererProps!.data).toEqual({ name: "Ada" });

    rerender(React.createElement(Renderer, { data: chatDataNamed("Bob") }));
    await waitFor(() =>
      expect(lastRendererProps!.data).toEqual({ name: "Bob" }),
    );
  });

  it("preserves user edits across a re-render with the same surface identity", async () => {
    const fetchMock = vi.fn(async (p: string) => {
      if (p === "/tools/render_ui/config") {
        return {
          ok: true,
          json: async () => ({ interactivity: "editable" }),
        } as unknown as Response;
      }
      return { ok: true, json: async () => ({}) } as unknown as Response;
    });
    const Renderer = await loadBundle({ fetch: fetchMock });
    const { rerender } = render(
      React.createElement(Renderer, { data: chatDataNamed("Ada") }),
    );
    await waitFor(() =>
      expect(lastRendererProps?.onAction).toBeInstanceOf(Function),
    );

    // User edits the model in place.
    await act(async () => {
      (lastRendererProps!.onDataChange as (n: AnyRec) => void)({
        name: "Edited",
      });
    });
    await waitFor(() =>
      expect(lastRendererProps!.data).toEqual({ name: "Edited" }),
    );

    // Re-render with a fresh object of the SAME identity (same seed data):
    // the edit must survive — no spurious re-seed.
    rerender(React.createElement(Renderer, { data: chatDataNamed("Ada") }));
    await waitFor(() =>
      expect(lastRendererProps?.onAction).toBeInstanceOf(Function),
    );
    expect(lastRendererProps!.data).toEqual({ name: "Edited" });
  });
});
