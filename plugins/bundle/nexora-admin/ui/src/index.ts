/**
 * Nexora Admin frontend plugin for QwenPaw.
 *
 * Enterprise admin surface (Fase 3): registers the Audit Logs page at
 * `/nexora/audit` plus a sidebar menu entry under the Settings bucket.
 * Visibility is gated by the `audit.view` permission resolved from
 * `GET /api/auth/me` (effective permissions). The route itself is always
 * registered — the backend enforces RBAC on `GET /api/nexora/audit`.
 *
 * No React/antd is bundled: everything comes from `window.QwenPaw.host`,
 * mirroring the a2ui-chat / cloudpaw plugin recipe. The file deliberately
 * avoids JSX so the same source runs through the plugin's own vite lib
 * build and the console's vitest pipeline without a JSX-runtime import.
 */

type AnyRec = Record<string, unknown>;
type HostReact = AnyRec & {
  createElement: (...args: any[]) => unknown;
  useCallback: <T extends (...args: any[]) => any>(fn: T, deps: unknown[]) => T;
  useEffect: (effect: () => void | (() => void), deps?: unknown[]) => void;
  useState: <T>(
    initial: T | (() => T),
  ) => [T, (value: T | ((previous: T) => T)) => void];
};

const PLUGIN_ID = "nexora-admin";

export interface AuditEvent {
  id: string;
  timestamp: number;
  actor: string;
  action: string;
  status: string;
  resource_type?: string;
  resource_id?: string;
  ip?: string;
  user_agent?: string;
  detail?: Record<string, unknown>;
}

// ─────────────────────────────────────────────────────────────────────────────
// i18n — pt-BR first, en + zh fallbacks (locale comes from the host)
// ─────────────────────────────────────────────────────────────────────────────

const MESSAGES: Record<string, Record<string, string>> = {
  "pt-BR": {
    menuLabel: "Auditoria",
    title: "Auditoria",
    subtitle:
      "Logins, operações da plataforma e bloqueios de permissão, para rastreabilidade e segurança.",
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
    statusStarted: "Em execução",
  },
  en: {
    menuLabel: "Audit Logs",
    title: "Audit Logs",
    subtitle:
      "Logins, platform operations and permission denials, for traceability and security.",
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
    statusStarted: "Running",
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
    statusStarted: "执行中",
  },
};

const ACTION_LABELS: Record<string, Record<string, string>> = {
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
    "chat.file.upload": "Upload de anexo",
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
    "chat.file.upload": "File upload",
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
    "chat.file.upload": "上传附件",
  },
};

const STATUS_COLORS: Record<string, string> = {
  success: "green",
  failure: "red",
  denied: "orange",
  started: "blue",
};

function normalizeLocale(locale: string | undefined): string {
  if (!locale) return "pt-BR";
  if (locale.startsWith("pt")) return "pt-BR";
  if (locale.startsWith("zh")) return "zh";
  if (MESSAGES[locale]) return locale;
  return "en";
}

/** Sync locale read for non-React call sites (menu label). */
function currentLocale(): string {
  try {
    return normalizeLocale(
      localStorage.getItem("language") || navigator.language,
    );
  } catch {
    return "pt-BR";
  }
}

function msg(locale: string, key: string): string {
  return MESSAGES[locale]?.[key] ?? MESSAGES["pt-BR"][key] ?? key;
}

function actionLabel(locale: string, action: string): string {
  return ACTION_LABELS[locale]?.[action] ?? action;
}

function statusLabel(locale: string, status: string): string {
  const key =
    "status" + status.charAt(0).toUpperCase() + status.slice(1).toLowerCase();
  return MESSAGES[locale]?.[key] ?? MESSAGES["pt-BR"][key] ?? status;
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

function formatTime(timestamp: number): string {
  if (!timestamp) return "-";
  return new Date(timestamp * 1000).toLocaleString();
}

function toText(value: unknown): string {
  if (value === null || value === undefined) return "-";
  if (typeof value === "object") {
    try {
      return JSON.stringify(value, null, 2);
    } catch {
      return String(value);
    }
  }
  return String(value);
}

/** Short, single-line summary for the table row. */
function detailSummary(locale: string, event: AuditEvent): string {
  const d = event.detail || {};
  const keys = Object.keys(d);
  if (event.action === "chat.message.send") {
    return String(d.message_preview ?? "-");
  }
  if (event.action === "api.mutate") {
    return `${d.method ?? ""} ${event.resource_id ?? ""}`.trim() || "-";
  }
  if (event.action === "api.denied") {
    const perm = d.permission
      ? ` (${msg(locale, "permissionNeeded")}: ${d.permission})`
      : "";
    return `${d.method ?? ""} ${event.resource_id ?? ""}${perm}`.trim() || "-";
  }
  if (event.action === "page.view") {
    return String(d.title ?? event.resource_id ?? "-");
  }
  if (event.action === "agent.tool.execute") {
    const parts: string[] = [];
    if (d.agent_id) parts.push(String(d.agent_id));
    if (d.reason) parts.push(String(d.reason));
    if (d.error) parts.push(String(d.error));
    return parts.join(" | ") || "-";
  }
  if (keys.length === 0) return "-";
  return keys
    .slice(0, 3)
    .map(
      (k) => `${k}: ${typeof d[k] === "object" ? JSON.stringify(d[k]) : d[k]}`,
    )
    .join(" | ");
}

async function fetchPermissions(host: AnyRec): Promise<Set<string>> {
  const fetcher = host.fetch as
    | ((p: string, init?: RequestInit) => Promise<Response>)
    | undefined;
  if (typeof fetcher !== "function") return new Set();
  try {
    const res = await fetcher("/auth/me");
    if (!res.ok) return new Set();
    const me = (await res.json()) as { permissions?: string[] };
    return new Set(Array.isArray(me?.permissions) ? me.permissions : []);
  } catch {
    return new Set();
  }
}

// Module-level permission cache so menu `visible()` stays synchronous.
const state = { permissions: new Set<string>() };

// ─────────────────────────────────────────────────────────────────────────────
// Page factory — pulls React/antd from the host at call time
// ─────────────────────────────────────────────────────────────────────────────

function buildAuditLogsPage(): ((props: AnyRec) => unknown) | null {
  const QP = (window as unknown as AnyRec).QwenPaw as AnyRec | undefined;
  const host = QP?.host as AnyRec | undefined;
  if (!host) return null;
  const React = host.React as HostReact;
  const antd = host.antd as AnyRec;
  const antdIcons = (host.antdIcons as AnyRec) || {};
  if (!React || !antd) return null;

  const h = React.createElement;
  const {
    Button,
    Card,
    DatePicker,
    Descriptions,
    Drawer,
    Empty,
    Form,
    Input,
    Select,
    Space,
    Table,
    Tag,
    Typography,
  } = antd as AnyRec as Record<string, any>;
  const { ReloadOutlined, InfoCircleOutlined } = antdIcons as Record<
    string,
    any
  >;
  const RangePicker = DatePicker?.RangePicker;

  interface Filters {
    actor?: string;
    action?: string;
    status?: string;
    date_from?: string;
    date_to?: string;
    limit: number;
  }

  function buildQuery(f: Filters): string {
    const q = new URLSearchParams();
    if (f.actor) q.set("actor", f.actor);
    if (f.action) q.set("action", f.action);
    if (f.status) q.set("status", f.status);
    if (f.date_from) q.set("date_from", f.date_from);
    if (f.date_to) q.set("date_to", f.date_to);
    q.set("limit", String(f.limit || 200));
    return `?${q.toString()}`;
  }

  function DetailContent({
    event,
    locale,
  }: {
    event: AuditEvent;
    locale: string;
  }) {
    const base: Array<{ label: string; value: string; copyable?: boolean }> = [
      { label: msg(locale, "eventId"), value: event.id, copyable: true },
      { label: msg(locale, "time"), value: formatTime(event.timestamp) },
      { label: msg(locale, "user"), value: event.actor || "-" },
      {
        label: msg(locale, "action"),
        value: actionLabel(locale, event.action),
      },
      {
        label: msg(locale, "status"),
        value: statusLabel(locale, event.status),
      },
      { label: msg(locale, "resource"), value: event.resource_id || "-" },
      { label: msg(locale, "sourceIp"), value: event.ip || "-" },
    ];
    if (event.user_agent) {
      base.push({ label: msg(locale, "userAgent"), value: event.user_agent });
    }
    const detail = event.detail || {};
    const contextItems = Object.keys(detail).map((k) => ({
      label: k,
      value: toText(detail[k]),
    }));

    return h(
      "div",
      null,
      h(
        Descriptions,
        {
          title: msg(locale, "baseInfo"),
          column: 2,
          bordered: true,
          size: "small",
          style: { marginBottom: 16 },
        },
        ...base.map((item) =>
          h(
            Descriptions.Item,
            {
              key: item.label,
              label: item.label,
              span: item.label === msg(locale, "userAgent") ? 2 : 1,
            },
            h(
              Typography.Text,
              { copyable: item.copyable === true },
              item.value,
            ),
          ),
        ),
      ),
      contextItems.length > 0
        ? h(
            Descriptions,
            {
              title: msg(locale, "context"),
              column: 1,
              bordered: true,
              size: "small",
            },
            ...contextItems.map((item) =>
              h(
                Descriptions.Item,
                { key: item.label, label: item.label },
                item.value.length > 200
                  ? h(
                      Typography.Paragraph,
                      {
                        style: {
                          marginBottom: 0,
                          maxHeight: 300,
                          overflow: "auto",
                          whiteSpace: "pre-wrap",
                        },
                      },
                      item.value,
                    )
                  : h(Typography.Text, null, item.value),
              ),
            ),
          )
        : null,
    );
  }

  function AuditLogsPage() {
    const useLocale = host!.useLocale as (() => string) | undefined;
    const rawLocale =
      typeof useLocale === "function" ? useLocale() : currentLocale();
    const locale = normalizeLocale(rawLocale);

    const [events, setEvents] = React.useState<AuditEvent[]>([]);
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);
    const [drawerEvent, setDrawerEvent] = React.useState<AuditEvent | null>(
      null,
    );
    const [filters, setFilters] = React.useState<Filters>({ limit: 200 });
    const [range, setRange] = React.useState<[string, string] | null>(null);

    const load = React.useCallback(
      async (f: Filters) => {
        const fetcher = host!.fetch as
          | ((p: string, init?: RequestInit) => Promise<Response>)
          | undefined;
        if (typeof fetcher !== "function") return;
        setLoading(true);
        setError(null);
        try {
          const res = await fetcher(`/nexora/audit${buildQuery(f)}`);
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          const data = (await res.json()) as AuditEvent[];
          setEvents(Array.isArray(data) ? data : []);
        } catch {
          setEvents([]);
          setError(msg(locale, "loadFailed"));
        } finally {
          setLoading(false);
        }
      },
      [locale],
    );

    React.useEffect(() => {
      void load({ limit: 200 });
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const submit = () => {
      const f: Filters = {
        ...filters,
        date_from: range?.[0] || undefined,
        date_to: range?.[1] || undefined,
      };
      void load(f);
    };

    const columns = [
      {
        title: msg(locale, "time"),
        dataIndex: "timestamp",
        key: "timestamp",
        width: 170,
        render: (v: number) => formatTime(v),
      },
      {
        title: msg(locale, "user"),
        dataIndex: "actor",
        key: "actor",
        width: 120,
        render: (v: string) => h(Typography.Text, { strong: true }, v || "-"),
      },
      {
        title: msg(locale, "action"),
        dataIndex: "action",
        key: "action",
        width: 170,
        render: (v: string) => actionLabel(locale, v),
      },
      {
        title: msg(locale, "status"),
        dataIndex: "status",
        key: "status",
        width: 100,
        render: (v: string) =>
          h(
            Tag,
            { color: STATUS_COLORS[v] || "default" },
            statusLabel(locale, v),
          ),
      },
      {
        title: msg(locale, "resource"),
        key: "resource",
        width: 180,
        ellipsis: true,
        render: (_: unknown, record: AuditEvent) =>
          h(
            Space,
            { direction: "vertical", size: 0 },
            h(Typography.Text, { ellipsis: true }, record.resource_id || "-"),
            h(
              Typography.Text,
              { type: "secondary", style: { fontSize: 12 } },
              record.resource_type || "-",
            ),
          ),
      },
      {
        title: msg(locale, "summary"),
        key: "summary",
        ellipsis: true,
        render: (_: unknown, record: AuditEvent) =>
          h(
            Typography.Text,
            { ellipsis: true, style: { maxWidth: 320 } },
            detailSummary(locale, record),
          ),
      },
      {
        title: "IP",
        dataIndex: "ip",
        key: "ip",
        width: 130,
        render: (v: string) => v || "-",
      },
      {
        title: "",
        key: "actions",
        width: 50,
        render: (_: unknown, record: AuditEvent) =>
          h(Button, {
            type: "link",
            size: "small",
            "aria-label": msg(locale, "details"),
            icon: InfoCircleOutlined ? h(InfoCircleOutlined) : undefined,
            onClick: () => setDrawerEvent(record),
          }),
      },
    ];

    const actionOptions = Object.keys(
      ACTION_LABELS[locale] ?? ACTION_LABELS["pt-BR"],
    ).map((value) => ({ value, label: actionLabel(locale, value) }));

    const statusOptions = ["success", "failure", "denied", "started"].map(
      (value) => ({ value, label: statusLabel(locale, value) }),
    );

    return h(
      "div",
      { style: { padding: "0 16px 24px" } },
      // Header
      h(
        "div",
        {
          style: {
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            gap: 12,
            flexWrap: "wrap",
            margin: "20px 0 16px",
          },
        },
        h(
          "div",
          null,
          h(
            Typography.Title,
            { level: 4, style: { margin: 0 } },
            msg(locale, "title"),
          ),
          h(
            Typography.Text,
            { type: "secondary" },
            msg(locale, "subtitle"),
            events.length > 0
              ? ` ${events.length} ${msg(locale, "showing")}.`
              : "",
          ),
        ),
        h(
          Button,
          {
            icon: ReloadOutlined ? h(ReloadOutlined) : undefined,
            onClick: submit,
            loading,
          },
          msg(locale, "refresh"),
        ),
      ),
      // Filters
      h(
        Card,
        { style: { marginBottom: 16 } },
        h(
          Form,
          {
            layout: "inline",
            onFinish: submit,
            style: { rowGap: 8, columnGap: 8, flexWrap: "wrap" },
          },
          h(
            Form.Item,
            { label: msg(locale, "user") },
            h(Input, {
              allowClear: true,
              placeholder: msg(locale, "userPlaceholder"),
              style: { width: 140 },
              value: filters.actor,
              onChange: (e: { target: { value: string } }) =>
                setFilters((f: Filters) => ({
                  ...f,
                  actor: e.target.value || undefined,
                })),
            }),
          ),
          h(
            Form.Item,
            { label: msg(locale, "action") },
            h(Select, {
              allowClear: true,
              placeholder: msg(locale, "all"),
              style: { width: 200 },
              options: actionOptions,
              value: filters.action,
              onChange: (v: string | undefined) =>
                setFilters((f: Filters) => ({ ...f, action: v })),
            }),
          ),
          h(
            Form.Item,
            { label: msg(locale, "status") },
            h(Select, {
              allowClear: true,
              placeholder: msg(locale, "all"),
              style: { width: 130 },
              options: statusOptions,
              value: filters.status,
              onChange: (v: string | undefined) =>
                setFilters((f: Filters) => ({ ...f, status: v })),
            }),
          ),
          RangePicker
            ? h(
                Form.Item,
                { label: msg(locale, "timeRange") },
                h(RangePicker, {
                  onChange: (
                    _dates: unknown,
                    dateStrings: [string, string],
                  ) => {
                    if (!dateStrings || (!dateStrings[0] && !dateStrings[1])) {
                      setRange(null);
                    } else {
                      setRange(dateStrings);
                    }
                  },
                }),
              )
            : null,
          h(
            Form.Item,
            { label: msg(locale, "limit") },
            h(Select, {
              style: { width: 90 },
              value: filters.limit,
              options: [100, 200, 500, 1000].map((v) => ({
                value: v,
                label: String(v),
              })),
              onChange: (v: number) =>
                setFilters((f: Filters) => ({ ...f, limit: v })),
            }),
          ),
          h(
            Form.Item,
            null,
            h(
              Button,
              { type: "primary", htmlType: "submit", loading },
              msg(locale, "search"),
            ),
          ),
        ),
      ),
      // Table
      h(
        Card,
        null,
        error
          ? h(
              "div",
              { style: { marginBottom: 12 } },
              h(Typography.Text, { type: "danger" }, error),
            )
          : null,
        h(Table, {
          rowKey: (r: AuditEvent) =>
            r.id || `${r.timestamp}-${r.actor}-${r.action}`,
          columns,
          dataSource: events,
          loading,
          size: "middle",
          locale: {
            emptyText: h(Empty, {
              image: Empty.PRESENTED_IMAGE_SIMPLE,
              description: msg(locale, "empty"),
            }),
          },
          pagination: {
            pageSize: 20,
            showSizeChanger: true,
            showTotal: (total: number) => `${total} ${msg(locale, "total")}`,
          },
          scroll: { x: 900 },
        }),
      ),
      // Detail drawer
      h(
        Drawer,
        {
          title: msg(locale, "detailsTitle"),
          placement: "right",
          width: 640,
          open: !!drawerEvent,
          onClose: () => setDrawerEvent(null),
          destroyOnClose: true,
        },
        drawerEvent ? h(DetailContent, { event: drawerEvent, locale }) : null,
      ),
    );
  }

  return AuditLogsPage as unknown as (props: AnyRec) => unknown;
}

// ─────────────────────────────────────────────────────────────────────────────
// Install
// ─────────────────────────────────────────────────────────────────────────────

async function install(): Promise<void> {
  const QP = (window as unknown as AnyRec).QwenPaw as AnyRec | undefined;
  if (!QP) return;
  const host = QP.host as AnyRec | undefined;
  const route = QP.route as
    | { add: (pluginId: string, route: AnyRec) => unknown }
    | undefined;
  const menu = QP.menu as
    | { add: (pluginId: string, item: AnyRec) => unknown }
    | undefined;
  if (!host || !route || !menu) return;

  const AuditLogsPage = buildAuditLogsPage();
  if (!AuditLogsPage) return;

  // Route is always available; the backend enforces audit.view via RBAC.
  route.add(PLUGIN_ID, {
    id: "nexora-admin.audit",
    path: "/nexora/audit",
    component: AuditLogsPage,
  });

  // Menu entry only after we know the user's effective permissions, so the
  // sidebar re-renders (registry notify) with `visible()` already correct.
  state.permissions = await fetchPermissions(host);
  if (!state.permissions.has("audit.view")) return;

  const React = host.React as HostReact | undefined;
  const antdIcons = (host.antdIcons as AnyRec) || {};
  const AuditOutlined = antdIcons.AuditOutlined as
    | ((props: AnyRec) => unknown)
    | undefined;

  menu.add(PLUGIN_ID, {
    id: "nexora-admin.audit",
    location: "primary.settings",
    parentId: "core.settings-group",
    label: () => msg(currentLocale(), "menuLabel"),
    icon:
      React && AuditOutlined
        ? React.createElement(
            AuditOutlined as never,
            {
              style: { fontSize: 16 },
            } as never,
          )
        : undefined,
    route: "nexora-admin.audit",
    order: 62, // after Security (60), before Token Usage (70)
    visible: () => state.permissions.has("audit.view"),
  });
}

void install();

// Exported for tests.
export { install, fetchPermissions, buildAuditLogsPage, state };
