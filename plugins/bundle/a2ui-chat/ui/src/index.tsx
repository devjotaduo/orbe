/**
 * A2UI Chat frontend plugin for QwenPaw.
 *
 * Registers the `render_ui` tool renderer: parses the tool's JSON output
 * ({ surface: [...A2UI messages] }) into an A2uiSurface and renders it
 * read-only via the host's `A2uiRenderer`. React, the renderer and the
 * surface reducer all come from the host (window.QwenPaw.host) — this
 * bundle ships no React/antd of its own.
 */
type AnyRec = Record<string, unknown>;

interface SurfaceMsg {
  messageType: string;
  surfaceId?: string;
}

// Minimal shapes for the bits of React we use. React itself comes from the
// host at runtime (window.QwenPaw.host.React); typing it locally keeps this
// bundle compilable WITHOUT `react` being resolvable in every context that
// type-checks it (e.g. the console's `tsc -b`, where the plugin's own
// node_modules is not installed).
interface ReactLike {
  createElement: (
    type: unknown,
    props?: AnyRec | null,
    ...children: unknown[]
  ) => unknown;
  useMemo: <T>(factory: () => T, deps: unknown[]) => T;
  useState: <T>(initial: T) => [T, (next: T) => void];
  useEffect: (effect: () => void | (() => void), deps: unknown[]) => void;
}
type FCLike = (props: AnyRec) => unknown;

/** Pull the render_ui tool's string output out of the chat `data` prop. */
function extractToolOutput(data: AnyRec): unknown {
  const content = data?.content as AnyRec[] | undefined;
  if (!Array.isArray(content)) return undefined;
  // The result block is appended after the call block (index 1+).
  const result = content[1]?.data as AnyRec | undefined;
  if (result && "output" in result) return result.output;
  // Fallback: scan for the first block carrying `.data.output`.
  for (const block of content) {
    const bd = block?.data as AnyRec | undefined;
    if (bd && "output" in bd) return bd.output;
  }
  return undefined;
}

/** Build an A2uiSurface from the tool output, or null if unusable. */
function parseSurface(output: unknown): AnyRec | null {
  const QP = (window as unknown as AnyRec).QwenPaw as AnyRec | undefined;
  const host = QP?.host as AnyRec | undefined;
  if (!host) return null;
  const apply = host.applyA2uiMessage as
    | ((s: AnyRec, m: SurfaceMsg) => AnyRec)
    | undefined;
  const empty = host.emptySurface as ((id: string) => AnyRec) | undefined;
  if (typeof apply !== "function" || typeof empty !== "function") return null;

  let raw: unknown;
  try {
    raw = typeof output === "string" ? JSON.parse(output) : output;
  } catch {
    return null;
  }
  if (!raw || typeof raw !== "object") return null;

  const msgs = ((raw as AnyRec).surface ?? raw) as unknown;
  if (!Array.isArray(msgs)) return null;

  let surf = empty("chat");
  for (const m of msgs) {
    if (m && typeof m === "object") surf = apply(surf, m as SurfaceMsg);
  }
  return surf;
}

/**
 * Read the `interactivity` config for the render_ui tool from the host.
 *
 * The real source is the tool-config endpoint
 * (`GET /api/tools/render_ui/config`), reached via the auth-aware
 * `host.fetch`. There is no global `window.QwenPaw.config` object — the
 * tool renderer only receives `{ data }`. On any failure we fall back to
 * the safe default `"read-only"`.
 */
async function fetchInteractivity(host: AnyRec): Promise<string> {
  const fetcher = host.fetch as
    | ((p: string, init?: AnyRec) => Promise<Response>)
    | undefined;
  if (typeof fetcher !== "function") return "read-only";
  try {
    const res = await fetcher("/tools/render_ui/config");
    if (!res.ok) return "read-only";
    const cfg = (await res.json()) as AnyRec;
    const value = cfg?.interactivity;
    return value === "editable" ? "editable" : "read-only";
  } catch {
    return "read-only";
  }
}

function A2uiToolRender({ data }: { data: AnyRec }) {
  const QP = (window as unknown as AnyRec).QwenPaw as AnyRec | undefined;
  const host = QP?.host as AnyRec | undefined;
  const React = host?.React as ReactLike | undefined;
  const Renderer = host?.A2uiRenderer as FCLike | undefined;

  if (!React) return null;

  const fallback = (msg: string) =>
    React.createElement(
      "div",
      {
        style: {
          color: "#cf1322",
          fontSize: 13,
          padding: "8px 12px",
          border: "1px solid #ffccc7",
          borderRadius: 6,
          background: "#fff2f0",
          margin: "4px 0",
        },
      },
      msg,
    );

  // Parse once per render of `data`; surface carries its own data model.
  const surf = React.useMemo(() => {
    const output = extractToolOutput(data);
    return parseSurface(output);
  }, [data]);

  // Editable data model lives in React state (seeded from the surface).
  const initialData = (surf?.data as AnyRec | undefined) ?? {};
  const [model, setModel] = React.useState<AnyRec>(initialData);

  // Resolve the configured interactivity (read-only by default).
  const [editable, setEditable] = React.useState(false);
  React.useEffect(() => {
    let alive = true;
    if (!host) return;
    fetchInteractivity(host).then((mode) => {
      if (alive) setEditable(mode === "editable");
    });
    return () => {
      alive = false;
    };
  }, [host]);

  if (!Renderer) return fallback("A2UI: renderer indisponível no host");
  if (!surf) return fallback("A2UI: surface inválida");

  const props: AnyRec = { surface: surf };
  if (editable) {
    props.data = model;
    props.onDataChange = (next: AnyRec) => setModel(next);
    props.onAction = async (name: string, params?: AnyRec) => {
      if (!host) return;
      const fetcher = host.fetch as
        | ((p: string, init?: AnyRec) => Promise<Response>)
        | undefined;
      if (typeof fetcher !== "function") return;
      const getSid = host.getCurrentSessionId as
        | (() => string | null)
        | undefined;
      const sid = (typeof getSid === "function" ? getSid() : null) ?? "chat";
      try {
        await fetcher("/a2ui/action", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: sid,
            action: name,
            data: model,
            params,
          }),
        });
      } catch {
        // Action delivery is best-effort; surface stays usable.
      }
    };
  }

  return React.createElement(Renderer, props);
}

function install() {
  const QP = (window as unknown as AnyRec).QwenPaw as AnyRec | undefined;
  if (!QP) return;
  const reg = QP.registerToolRender as
    | ((id: string, r: AnyRec) => void)
    | undefined;
  reg?.("a2ui-chat", { render_ui: A2uiToolRender });
}

install();
