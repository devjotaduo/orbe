function s(r) {
  var o;
  const n = r == null ? void 0 : r.content;
  if (!Array.isArray(n)) return;
  const t = (o = n[1]) == null ? void 0 : o.data;
  if (t && "output" in t) return t.output;
  for (const u of n) {
    const e = u == null ? void 0 : u.data;
    if (e && "output" in e) return e.output;
  }
}
function a(r) {
  const n = window.QwenPaw, t = n == null ? void 0 : n.host;
  if (!t) return null;
  const o = t.applyA2uiMessage, u = t.emptySurface;
  if (typeof o != "function" || typeof u != "function") return null;
  let e;
  try {
    e = typeof r == "string" ? JSON.parse(r) : r;
  } catch {
    return null;
  }
  if (!e || typeof e != "object") return null;
  const f = e.surface ?? e;
  if (!Array.isArray(f)) return null;
  let c = u("chat");
  for (const i of f)
    i && typeof i == "object" && (c = o(c, i));
  return c;
}
function l({ data: r }) {
  const n = window.QwenPaw, t = n == null ? void 0 : n.host, o = t == null ? void 0 : t.React, u = t == null ? void 0 : t.A2uiRenderer;
  if (!o) return null;
  const e = (i) => o.createElement(
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
  if (!u) return e("A2UI: renderer indisponível no host");
  const f = s(r), c = a(f);
  return c ? o.createElement(u, { surface: c }) : e("A2UI: surface inválida");
}
function p() {
  const r = window.QwenPaw;
  if (!r) return;
  const n = r.registerToolRender;
  n == null || n("a2ui-chat", { render_ui: l });
}
p();
