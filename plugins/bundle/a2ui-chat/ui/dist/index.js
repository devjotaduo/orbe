function g(r) {
  var n;
  const e = r == null ? void 0 : r.content;
  if (!Array.isArray(e)) return;
  const t = (n = e[1]) == null ? void 0 : n.data;
  if (t && "output" in t) return t.output;
  for (const i of e) {
    const o = i == null ? void 0 : i.data;
    if (o && "output" in o) return o.output;
  }
}
function m(r) {
  const e = window.QwenPaw, t = e == null ? void 0 : e.host;
  if (!t) return null;
  const n = t.applyA2uiMessage, i = t.emptySurface;
  if (typeof n != "function" || typeof i != "function") return null;
  let o;
  try {
    o = typeof r == "string" ? JSON.parse(r) : r;
  } catch {
    return null;
  }
  if (!o || typeof o != "object") return null;
  const a = o.surface ?? o;
  if (!Array.isArray(a)) return null;
  let u = i("chat");
  for (const s of a)
    s && typeof s == "object" && (u = n(u, s));
  return u;
}
async function v(r) {
  const e = r.fetch;
  if (typeof e != "function") return "read-only";
  try {
    const t = await e("/tools/render_ui/config");
    if (!t.ok) return "read-only";
    const n = await t.json();
    return (n == null ? void 0 : n.interactivity) === "editable" ? "editable" : "read-only";
  } catch {
    return "read-only";
  }
}
function A({ data: r }) {
  const e = window.QwenPaw, t = e == null ? void 0 : e.host, n = t == null ? void 0 : t.React, i = t == null ? void 0 : t.A2uiRenderer;
  if (!n) return null;
  const o = (c) => n.createElement(
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
    c
  ), a = n.useMemo(() => {
    const c = g(r);
    return m(c);
  }, [r]), u = (a == null ? void 0 : a.data) ?? {}, [s, y] = n.useState(u), [h, w] = n.useState(!1);
  if (n.useEffect(() => {
    let c = !0;
    if (t)
      return v(t).then((l) => {
        c && w(l === "editable");
      }), () => {
        c = !1;
      };
  }, [t]), !i) return o("A2UI: renderer indisponível no host");
  if (!a) return o("A2UI: surface inválida");
  const f = { surface: a };
  return h && (f.data = s, f.onDataChange = (c) => y(c), f.onAction = async (c, l) => {
    if (!t) return;
    const d = t.fetch;
    if (typeof d != "function") return;
    const p = t.getCurrentSessionId, b = (typeof p == "function" ? p() : null) ?? "chat";
    try {
      await d("/a2ui/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: b,
          action: c,
          data: s,
          params: l
        })
      });
    } catch {
    }
  }), n.createElement(i, f);
}
function S() {
  const r = window.QwenPaw;
  if (!r) return;
  const e = r.registerToolRender;
  e == null || e("a2ui-chat", { render_ui: A });
}
S();
