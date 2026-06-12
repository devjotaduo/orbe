function I(t) {
  var r;
  const e = t == null ? void 0 : t.content;
  if (!Array.isArray(e)) return;
  const n = (r = e[1]) == null ? void 0 : r.data;
  if (n && "output" in n) return n.output;
  for (const a of e) {
    const o = a == null ? void 0 : a.data;
    if (o && "output" in o) return o.output;
  }
}
function O(t) {
  const e = window.QwenPaw, n = e == null ? void 0 : e.host;
  if (!n) return null;
  const r = n.applyA2uiMessage, a = n.emptySurface;
  if (typeof r != "function" || typeof a != "function") return null;
  let o;
  try {
    o = typeof t == "string" ? JSON.parse(t) : t;
  } catch {
    return null;
  }
  if (!o || typeof o != "object") return null;
  const y = o.surface ?? o;
  if (!Array.isArray(y)) return null;
  let f = a("chat");
  for (const u of y)
    u && typeof u == "object" && (f = r(f, u));
  return f;
}
function j(t) {
  return t ? JSON.stringify({
    id: t.surfaceId ?? null,
    data: t.data ?? {}
  }) : null;
}
async function E(t) {
  const e = t.fetch;
  if (typeof e != "function") return "read-only";
  try {
    const n = await e("/tools/render_ui/config");
    if (!n.ok) return "read-only";
    const r = await n.json();
    return (r == null ? void 0 : r.interactivity) === "editable" ? "editable" : "read-only";
  } catch {
    return "read-only";
  }
}
function k(t) {
  const { useMemo: e, useState: n, useEffect: r, useRef: a, useCallback: o } = t;
  return function({ data: f }) {
    const u = window.QwenPaw, c = u == null ? void 0 : u.host, w = c == null ? void 0 : c.A2uiRenderer, s = e(() => {
      const i = I(f);
      return O(i);
    }, [f]), l = j(s), [p, g] = n(
      () => (s == null ? void 0 : s.data) ?? {}
    ), b = a(l);
    r(() => {
      l !== b.current && (b.current = l, g((s == null ? void 0 : s.data) ?? {}));
    }, [l]);
    const [v, R] = n(!1);
    r(() => {
      let i = !0;
      if (c)
        return E(c).then((h) => {
          i && R(h === "editable");
        }), () => {
          i = !1;
        };
    }, [c]);
    const T = o((i) => g(i), []), x = o(
      async (i, h) => {
        if (!c) return;
        const S = c.fetch;
        if (typeof S != "function") return;
        const m = c.getCurrentSessionId, C = (typeof m == "function" ? m() : null) ?? "chat";
        try {
          await S("/a2ui/action", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              session_id: C,
              action: i,
              data: p,
              params: h
            })
          });
        } catch {
        }
      },
      [c, p]
    ), A = (i) => t.createElement(
      "div",
      {
        style: {
          color: "#cf1322",
          fontSize: 13,
          padding: "8px 12px",
          border: "1px solid #ffccc7",
          borderRadius: 6,
          background: "#fff2f0",
          margin: "4px 0"
        }
      },
      i
    );
    if (!w) return A("A2UI: renderer indisponível no host");
    if (!s) return A("A2UI: surface inválida");
    const d = { surface: s };
    return v && (d.data = p, d.onDataChange = T, d.onAction = x), t.createElement(w, d);
  };
}
function J() {
  const t = window.QwenPaw;
  if (!t) return;
  const e = t.host, n = e == null ? void 0 : e.React, r = t.registerToolRender;
  !n || typeof r != "function" || r("a2ui-chat", { render_ui: k(n) });
}
J();
