/**
 * A2UI Chat frontend plugin for QwenPaw.
 *
 * Registers the `render_ui` tool renderer: parses the tool's JSON output
 * ({ surface: [...A2UI messages] }) into an A2uiSurface and renders it
 * read-only via the host's `A2uiRenderer`. React, the renderer and the
 * surface reducer all come from the host (window.QwenPaw.host) — this
 * bundle ships no React/antd of its own.
 *
 * The component is produced by `createA2uiToolRender(React)` so `React` is
 * captured in the closure and is always defined: every hook runs
 * unconditionally at the top of the component (no `if (!React) return null`
 * before the hooks), which keeps the Rules of Hooks satisfied even when the
 * same instance re-renders from an unusable surface to a real one.
 */
type AnyRec = Record<string, unknown>;

interface SurfaceMsg {
  messageType: string;
  surfaceId?: string;
}

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
 * Stable identity signature for a surface's seed data.
 *
 * Used to decide when the editable data model must be re-seeded: it changes
 * only when a *new* surface (different id or seed data) arrives, so a user's
 * in-progress edits — which live in `model` state, not on `surf` — are
 * preserved across renders that keep the same surface identity.
 */
function surfaceSeedKey(surf: AnyRec | null): string | null {
  if (!surf) return null;
  return JSON.stringify({
    id: (surf.surfaceId as string | undefined) ?? null,
    data: (surf.data as AnyRec | undefined) ?? {},
  });
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

/**
 * Build the tool renderer with `React` bound in the closure.
 *
 * Because `React` is a parameter here, the returned component never needs a
 * `if (!React) return null` guard before its hooks — all hooks run on every
 * render, regardless of whether the surface parsed. The only early returns
 * are the fallbacks *after* the hooks.
 */
function createA2uiToolRender(React: typeof import("react")) {
  const { useMemo, useState, useEffect, useRef, useCallback } = React;

  return function A2uiToolRender({ data }: { data: AnyRec }) {
    const QP = (window as unknown as AnyRec).QwenPaw as AnyRec | undefined;
    const host = QP?.host as AnyRec | undefined;
    const Renderer = host?.A2uiRenderer as React.FC<AnyRec> | undefined;

    // Parse once per render of `data`; surface carries its own data model.
    const surf = useMemo(() => {
      const output = extractToolOutput(data);
      return parseSurface(output);
    }, [data]);

    // Editable data model lives in React state (seeded from the surface).
    const seedKey = surfaceSeedKey(surf);
    const [model, setModel] = useState<AnyRec>(
      () => (surf?.data as AnyRec | undefined) ?? {},
    );

    // Re-seed the model only when the surface identity changes (a new/updated
    // surface on the same instance) — never on plain re-renders, so user
    // edits to `model` survive. Seeded once on mount via useState above.
    const seededRef = useRef<string | null>(seedKey);
    useEffect(() => {
      if (seedKey !== seededRef.current) {
        seededRef.current = seedKey;
        setModel((surf?.data as AnyRec | undefined) ?? {});
      }
      // `surf` is derived from `seedKey`; the signature is the real trigger.
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [seedKey]);

    // Resolve the configured interactivity (read-only by default).
    const [editable, setEditable] = useState(false);
    useEffect(() => {
      let alive = true;
      if (!host) return;
      fetchInteractivity(host).then((mode) => {
        if (alive) setEditable(mode === "editable");
      });
      return () => {
        alive = false;
      };
    }, [host]);

    const onDataChange = useCallback((next: AnyRec) => setModel(next), []);

    const onAction = useCallback(
      async (name: string, params?: AnyRec) => {
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
      },
      [host, model],
    );

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

    if (!Renderer) return fallback("A2UI: renderer indisponível no host");
    if (!surf) return fallback("A2UI: surface inválida");

    const props: AnyRec = { surface: surf };
    if (editable) {
      props.data = model;
      props.onDataChange = onDataChange;
      props.onAction = onAction;
    }

    return React.createElement(Renderer, props);
  };
}

function install() {
  const QP = (window as unknown as AnyRec).QwenPaw as AnyRec | undefined;
  if (!QP) return;
  const host = QP.host as AnyRec | undefined;
  const React = host?.React as typeof import("react") | undefined;
  const reg = QP.registerToolRender as
    | ((id: string, r: AnyRec) => void)
    | undefined;
  // Without React from the host there is nothing to render; bail quietly.
  if (!React || typeof reg !== "function") return;
  reg("a2ui-chat", { render_ui: createA2uiToolRender(React) });
}

install();
