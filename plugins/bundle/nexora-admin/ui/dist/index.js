const W = "nexora-admin", S = {
  "pt-BR": {
    menuLabel: "Auditoria",
    title: "Auditoria",
    subtitle: "Logins, operações da plataforma e bloqueios de permissão, para rastreabilidade e segurança.",
    showing: "registro(s) exibido(s)",
    refresh: "Atualizar",
    search: "Buscar",
    user: "Usuário",
    userPlaceholder: "nome de usuário",
    action: "Operação",
    status: "Resultado",
    all: "Todas",
    timeRange: "Período",
    limit: "Limite",
    time: "Data/Hora",
    resource: "Recurso",
    summary: "Resumo",
    details: "Detalhes",
    detailsTitle: "Detalhes do evento",
    eventId: "ID do evento",
    sourceIp: "IP de origem",
    userAgent: "Navegador",
    baseInfo: "Informações básicas",
    context: "Contexto da operação",
    loadFailed: "Falha ao carregar a auditoria",
    empty: "Nenhum evento de auditoria no período",
    total: "registros",
    permissionNeeded: "Permissão necessária",
    statusSuccess: "Sucesso",
    statusFailure: "Falha",
    statusDenied: "Negado",
    statusStarted: "Em execução"
  },
  en: {
    menuLabel: "Audit Logs",
    title: "Audit Logs",
    subtitle: "Logins, platform operations and permission denials, for traceability and security.",
    showing: "record(s) shown",
    refresh: "Refresh",
    search: "Search",
    user: "User",
    userPlaceholder: "username",
    action: "Action",
    status: "Status",
    all: "All",
    timeRange: "Time range",
    limit: "Limit",
    time: "Time",
    resource: "Resource",
    summary: "Summary",
    details: "Details",
    detailsTitle: "Event details",
    eventId: "Event ID",
    sourceIp: "Source IP",
    userAgent: "User agent",
    baseInfo: "Basic info",
    context: "Operation context",
    loadFailed: "Failed to load audit logs",
    empty: "No audit events in the selected period",
    total: "records",
    permissionNeeded: "Required permission",
    statusSuccess: "Success",
    statusFailure: "Failure",
    statusDenied: "Denied",
    statusStarted: "Running"
  },
  zh: {
    menuLabel: "日志审计",
    title: "日志审计",
    subtitle: "记录用户登录、平台操作和权限拦截，便于安全审计与问题追溯。",
    showing: "条记录",
    refresh: "刷新",
    search: "查询",
    user: "用户",
    userPlaceholder: "用户名",
    action: "操作",
    status: "结果",
    all: "全部",
    timeRange: "时间范围",
    limit: "数量",
    time: "时间",
    resource: "对象",
    summary: "摘要",
    details: "详情",
    detailsTitle: "审计事件详情",
    eventId: "事件 ID",
    sourceIp: "来源 IP",
    userAgent: "浏览器",
    baseInfo: "基本信息",
    context: "操作详情",
    loadFailed: "加载审计日志失败",
    empty: "所选时间段内没有审计事件",
    total: "条",
    permissionNeeded: "所需权限",
    statusSuccess: "成功",
    statusFailure: "失败",
    statusDenied: "拒绝",
    statusStarted: "执行中"
  }
}, k = {
  "pt-BR": {
    "auth.login": "Login",
    "auth.logout": "Logout",
    "auth.register": "Registro",
    "auth.profile.update": "Alteração de conta",
    "auth.revoke_all_tokens": "Revogar sessões",
    "page.view": "Acesso a página",
    "api.mutate": "Operação na plataforma",
    "api.denied": "Bloqueio de permissão",
    "chat.message.send": "Mensagem enviada",
    "agent.tool.execute": "Chamada de ferramenta",
    "chat.file.upload": "Upload de anexo"
  },
  en: {
    "auth.login": "Login",
    "auth.logout": "Logout",
    "auth.register": "Registration",
    "auth.profile.update": "Account update",
    "auth.revoke_all_tokens": "Revoke sessions",
    "page.view": "Page view",
    "api.mutate": "Platform operation",
    "api.denied": "Permission denied",
    "chat.message.send": "Message sent",
    "agent.tool.execute": "Tool call",
    "chat.file.upload": "File upload"
  },
  zh: {
    "auth.login": "登录",
    "auth.logout": "退出登录",
    "auth.register": "注册",
    "auth.profile.update": "修改账号",
    "auth.revoke_all_tokens": "注销全部会话",
    "page.view": "访问页面",
    "api.mutate": "平台操作",
    "api.denied": "权限拦截",
    "chat.message.send": "发送消息",
    "agent.tool.execute": "工具调用",
    "chat.file.upload": "上传附件"
  }
}, ne = {
  success: "green",
  failure: "red",
  denied: "orange",
  started: "blue"
};
function H(o) {
  return !o || o.startsWith("pt") ? "pt-BR" : o.startsWith("zh") ? "zh" : S[o] ? o : "en";
}
function Q() {
  try {
    return H(
      localStorage.getItem("language") || navigator.language
    );
  } catch {
    return "pt-BR";
  }
}
function s(o, i) {
  var t;
  return ((t = S[o]) == null ? void 0 : t[i]) ?? S["pt-BR"][i] ?? i;
}
function A(o, i) {
  var t;
  return ((t = k[o]) == null ? void 0 : t[i]) ?? i;
}
function P(o, i) {
  var c;
  const t = "status" + i.charAt(0).toUpperCase() + i.slice(1).toLowerCase();
  return ((c = S[o]) == null ? void 0 : c[t]) ?? S["pt-BR"][t] ?? i;
}
function q(o) {
  return o ? new Date(o * 1e3).toLocaleString() : "-";
}
function oe(o) {
  if (o == null) return "-";
  if (typeof o == "object")
    try {
      return JSON.stringify(o, null, 2);
    } catch {
      return String(o);
    }
  return String(o);
}
function re(o, i) {
  const t = i.detail || {}, c = Object.keys(t);
  if (i.action === "chat.message.send")
    return String(t.message_preview ?? "-");
  if (i.action === "api.mutate")
    return `${t.method ?? ""} ${i.resource_id ?? ""}`.trim() || "-";
  if (i.action === "api.denied") {
    const p = t.permission ? ` (${s(o, "permissionNeeded")}: ${t.permission})` : "";
    return `${t.method ?? ""} ${i.resource_id ?? ""}${p}`.trim() || "-";
  }
  if (i.action === "page.view")
    return String(t.title ?? i.resource_id ?? "-");
  if (i.action === "agent.tool.execute") {
    const p = [];
    return t.agent_id && p.push(String(t.agent_id)), t.reason && p.push(String(t.reason)), t.error && p.push(String(t.error)), p.join(" | ") || "-";
  }
  return c.length === 0 ? "-" : c.slice(0, 3).map(
    (p) => `${p}: ${typeof t[p] == "object" ? JSON.stringify(t[p]) : t[p]}`
  ).join(" | ");
}
async function le(o) {
  const i = o.fetch;
  if (typeof i != "function") return /* @__PURE__ */ new Set();
  try {
    const t = await i("/auth/me");
    if (!t.ok) return /* @__PURE__ */ new Set();
    const c = await t.json();
    return new Set(Array.isArray(c == null ? void 0 : c.permissions) ? c.permissions : []);
  } catch {
    return /* @__PURE__ */ new Set();
  }
}
const C = { permissions: /* @__PURE__ */ new Set() };
function ue() {
  const o = window.QwenPaw, i = o == null ? void 0 : o.host;
  if (!i) return null;
  const t = i.React, c = i.antd, p = i.antdIcons || {};
  if (!t || !c) return null;
  const e = t.createElement, {
    Button: I,
    Card: y,
    DatePicker: R,
    Descriptions: x,
    Drawer: J,
    Empty: E,
    Form: g,
    Input: K,
    Select: _,
    Space: V,
    Table: X,
    Tag: Y,
    Typography: m
  } = c, { ReloadOutlined: $, InfoCircleOutlined: O } = p, B = R == null ? void 0 : R.RangePicker;
  function Z(r) {
    const l = new URLSearchParams();
    return r.actor && l.set("actor", r.actor), r.action && l.set("action", r.action), r.status && l.set("status", r.status), r.date_from && l.set("date_from", r.date_from), r.date_to && l.set("date_to", r.date_to), l.set("limit", String(r.limit || 200)), `?${l.toString()}`;
  }
  function ee({
    event: r,
    locale: l
  }) {
    const n = [
      { label: s(l, "eventId"), value: r.id, copyable: !0 },
      { label: s(l, "time"), value: q(r.timestamp) },
      { label: s(l, "user"), value: r.actor || "-" },
      {
        label: s(l, "action"),
        value: A(l, r.action)
      },
      {
        label: s(l, "status"),
        value: P(l, r.status)
      },
      { label: s(l, "resource"), value: r.resource_id || "-" },
      { label: s(l, "sourceIp"), value: r.ip || "-" }
    ];
    r.user_agent && n.push({ label: s(l, "userAgent"), value: r.user_agent });
    const h = r.detail || {}, b = Object.keys(h).map((d) => ({
      label: d,
      value: oe(h[d])
    }));
    return e(
      "div",
      null,
      e(
        x,
        {
          title: s(l, "baseInfo"),
          column: 2,
          bordered: !0,
          size: "small",
          style: { marginBottom: 16 }
        },
        ...n.map(
          (d) => e(
            x.Item,
            {
              key: d.label,
              label: d.label,
              span: d.label === s(l, "userAgent") ? 2 : 1
            },
            e(
              m.Text,
              { copyable: d.copyable === !0 },
              d.value
            )
          )
        )
      ),
      b.length > 0 ? e(
        x,
        {
          title: s(l, "context"),
          column: 1,
          bordered: !0,
          size: "small"
        },
        ...b.map(
          (d) => e(
            x.Item,
            { key: d.label, label: d.label },
            d.value.length > 200 ? e(
              m.Paragraph,
              {
                style: {
                  marginBottom: 0,
                  maxHeight: 300,
                  overflow: "auto",
                  whiteSpace: "pre-wrap"
                }
              },
              d.value
            ) : e(m.Text, null, d.value)
          )
        )
      ) : null
    );
  }
  function te() {
    const r = i.useLocale, l = typeof r == "function" ? r() : Q(), n = H(l), [h, b] = t.useState([]), [d, D] = t.useState(!1), [z, F] = t.useState(null), [L, N] = t.useState(
      null
    ), [w, v] = t.useState({ limit: 200 }), [f, j] = t.useState(null), U = t.useCallback(
      async (a) => {
        const u = i.fetch;
        if (typeof u == "function") {
          D(!0), F(null);
          try {
            const T = await u(`/nexora/audit${Z(a)}`);
            if (!T.ok) throw new Error(`HTTP ${T.status}`);
            const M = await T.json();
            b(Array.isArray(M) ? M : []);
          } catch {
            b([]), F(s(n, "loadFailed"));
          } finally {
            D(!1);
          }
        }
      },
      [n]
    );
    t.useEffect(() => {
      U({ limit: 200 });
    }, []);
    const G = () => {
      const a = {
        ...w,
        date_from: (f == null ? void 0 : f[0]) || void 0,
        date_to: (f == null ? void 0 : f[1]) || void 0
      };
      U(a);
    }, ae = [
      {
        title: s(n, "time"),
        dataIndex: "timestamp",
        key: "timestamp",
        width: 170,
        render: (a) => q(a)
      },
      {
        title: s(n, "user"),
        dataIndex: "actor",
        key: "actor",
        width: 120,
        render: (a) => e(m.Text, { strong: !0 }, a || "-")
      },
      {
        title: s(n, "action"),
        dataIndex: "action",
        key: "action",
        width: 170,
        render: (a) => A(n, a)
      },
      {
        title: s(n, "status"),
        dataIndex: "status",
        key: "status",
        width: 100,
        render: (a) => e(
          Y,
          { color: ne[a] || "default" },
          P(n, a)
        )
      },
      {
        title: s(n, "resource"),
        key: "resource",
        width: 180,
        ellipsis: !0,
        render: (a, u) => e(
          V,
          { direction: "vertical", size: 0 },
          e(m.Text, { ellipsis: !0 }, u.resource_id || "-"),
          e(
            m.Text,
            { type: "secondary", style: { fontSize: 12 } },
            u.resource_type || "-"
          )
        )
      },
      {
        title: s(n, "summary"),
        key: "summary",
        ellipsis: !0,
        render: (a, u) => e(
          m.Text,
          { ellipsis: !0, style: { maxWidth: 320 } },
          re(n, u)
        )
      },
      {
        title: "IP",
        dataIndex: "ip",
        key: "ip",
        width: 130,
        render: (a) => a || "-"
      },
      {
        title: "",
        key: "actions",
        width: 50,
        render: (a, u) => e(I, {
          type: "link",
          size: "small",
          "aria-label": s(n, "details"),
          icon: O ? e(O) : void 0,
          onClick: () => N(u)
        })
      }
    ], se = Object.keys(
      k[n] ?? k["pt-BR"]
    ).map((a) => ({ value: a, label: A(n, a) })), ie = ["success", "failure", "denied", "started"].map(
      (a) => ({ value: a, label: P(n, a) })
    );
    return e(
      "div",
      { style: { padding: "0 16px 24px" } },
      // Header
      e(
        "div",
        {
          style: {
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            gap: 12,
            flexWrap: "wrap",
            margin: "20px 0 16px"
          }
        },
        e(
          "div",
          null,
          e(
            m.Title,
            { level: 4, style: { margin: 0 } },
            s(n, "title")
          ),
          e(
            m.Text,
            { type: "secondary" },
            s(n, "subtitle"),
            h.length > 0 ? ` ${h.length} ${s(n, "showing")}.` : ""
          )
        ),
        e(
          I,
          {
            icon: $ ? e($) : void 0,
            onClick: G,
            loading: d
          },
          s(n, "refresh")
        )
      ),
      // Filters
      e(
        y,
        { style: { marginBottom: 16 } },
        e(
          g,
          {
            layout: "inline",
            onFinish: G,
            style: { rowGap: 8, columnGap: 8, flexWrap: "wrap" }
          },
          e(
            g.Item,
            { label: s(n, "user") },
            e(K, {
              allowClear: !0,
              placeholder: s(n, "userPlaceholder"),
              style: { width: 140 },
              value: w.actor,
              onChange: (a) => v((u) => ({
                ...u,
                actor: a.target.value || void 0
              }))
            })
          ),
          e(
            g.Item,
            { label: s(n, "action") },
            e(_, {
              allowClear: !0,
              placeholder: s(n, "all"),
              style: { width: 200 },
              options: se,
              value: w.action,
              onChange: (a) => v((u) => ({ ...u, action: a }))
            })
          ),
          e(
            g.Item,
            { label: s(n, "status") },
            e(_, {
              allowClear: !0,
              placeholder: s(n, "all"),
              style: { width: 130 },
              options: ie,
              value: w.status,
              onChange: (a) => v((u) => ({ ...u, status: a }))
            })
          ),
          B ? e(
            g.Item,
            { label: s(n, "timeRange") },
            e(B, {
              onChange: (a, u) => {
                !u || !u[0] && !u[1] ? j(null) : j(u);
              }
            })
          ) : null,
          e(
            g.Item,
            { label: s(n, "limit") },
            e(_, {
              style: { width: 90 },
              value: w.limit,
              options: [100, 200, 500, 1e3].map((a) => ({
                value: a,
                label: String(a)
              })),
              onChange: (a) => v((u) => ({ ...u, limit: a }))
            })
          ),
          e(
            g.Item,
            null,
            e(
              I,
              { type: "primary", htmlType: "submit", loading: d },
              s(n, "search")
            )
          )
        )
      ),
      // Table
      e(
        y,
        null,
        z ? e(
          "div",
          { style: { marginBottom: 12 } },
          e(m.Text, { type: "danger" }, z)
        ) : null,
        e(X, {
          rowKey: (a) => a.id || `${a.timestamp}-${a.actor}-${a.action}`,
          columns: ae,
          dataSource: h,
          loading: d,
          size: "middle",
          locale: {
            emptyText: e(E, {
              image: E.PRESENTED_IMAGE_SIMPLE,
              description: s(n, "empty")
            })
          },
          pagination: {
            pageSize: 20,
            showSizeChanger: !0,
            showTotal: (a) => `${a} ${s(n, "total")}`
          },
          scroll: { x: 900 }
        })
      ),
      // Detail drawer
      e(
        J,
        {
          title: s(n, "detailsTitle"),
          placement: "right",
          width: 640,
          open: !!L,
          onClose: () => N(null),
          destroyOnClose: !0
        },
        L ? e(ee, { event: L, locale: n }) : null
      )
    );
  }
  return te;
}
async function de() {
  const o = window.QwenPaw;
  if (!o) return;
  const i = o.host, t = o.route, c = o.menu;
  if (!i || !t || !c) return;
  const p = ue();
  if (!p || (t.add(W, {
    id: "nexora-admin.audit",
    path: "/nexora/audit",
    component: p
  }), C.permissions = await le(i), !C.permissions.has("audit.view"))) return;
  const e = i.React, y = (i.antdIcons || {}).AuditOutlined;
  c.add(W, {
    id: "nexora-admin.audit",
    location: "primary.settings",
    parentId: "core.settings-group",
    label: () => s(Q(), "menuLabel"),
    icon: e && y ? e.createElement(
      y,
      {
        style: { fontSize: 16 }
      }
    ) : void 0,
    route: "nexora-admin.audit",
    order: 62,
    // after Security (60), before Token Usage (70)
    visible: () => C.permissions.has("audit.view")
  });
}
de();
export {
  ue as buildAuditLogsPage,
  le as fetchPermissions,
  de as install,
  C as state
};
