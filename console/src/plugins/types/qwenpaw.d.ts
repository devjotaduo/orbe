/**
 * plugins/types/qwenpaw.d.ts — stable public contract for plugin authors.
 *
 * Plugin TS projects (cloudpaw, qwenpaw-pet, …) should COPY this file into
 * their own `qwenpaw-host.d.ts` and uncomment the `declare global` block at
 * the bottom. We intentionally do NOT re-export `IAgentScopeRuntimeWebUIOptions`
 * so the public surface stays stable across vendor upgrades.
 *
 * Inside the host, the global `Window.QwenPaw` is declared in
 * `console/src/plugins/hostExternals.ts` — keep that the single source
 * of truth to avoid duplicate-declaration conflicts.
 *
 * ─────────────────────────────────────────────────────────────────────────
 * Three verbs cover every chat customization intent:
 *   set(pluginId, partial)  → shallow-merge specific option fields
 *   render(pluginId, node)  → whole-section replacement (welcome / leftHeader)
 *   add(pluginId, item)     → append to additive lists
 * ─────────────────────────────────────────────────────────────────────────
 */
import type React from "react";

export type Localized<T> = T | ((locale: string) => T);

export interface Disposable {
  dispose(): void;
}

export type HostThemeMode = "light" | "dark";

export interface HostAgentInfo {
  id: string;
}

export interface HostSessionInfo {
  id: string;
}

// ── A2UI generative UI (read-only surfaces rendered in chat bubbles) ─────────
// Mirror of `console/src/api/types/a2ui.ts` (itself a mirror of the backend
// `src/qwenpaw/a2ui/schema.py`). Kept inline so this public contract stays
// self-contained for plugin authors who copy it.

export interface A2uiComponent {
  id: string;
  type: string;
  properties: Record<string, unknown>;
  children: string[];
}

export type A2uiMessage =
  | { messageType: "createSurface"; surfaceId: string; root: string }
  | {
      messageType: "updateComponents";
      surfaceId: string;
      components: A2uiComponent[];
    }
  | {
      messageType: "updateDataModel";
      surfaceId: string;
      data: Record<string, unknown>;
    }
  | { messageType: "deleteSurface"; surfaceId: string };

export interface A2uiSurface {
  surfaceId: string;
  /** id of the root component (empty until createSurface arrives) */
  root: string;
  /** id -> component */
  components: Record<string, A2uiComponent>;
  /** raw data model carried by updateDataModel (reserved for binding) */
  data: Record<string, unknown>;
}

export interface A2uiRendererProps {
  surface: A2uiSurface;
  /** Data model to resolve binds against. Defaults to `surface.data`. */
  data?: Record<string, unknown>;
  /** Called with the next data model when an editable field changes. */
  onDataChange?: (next: Record<string, unknown>) => void;
  /** Called when a Button carrying `properties.action` is activated. */
  onAction?: (name: string, params?: Record<string, unknown>) => void;
}

export interface ChatPromptItem {
  label?: React.ReactNode;
  value: string;
}

export interface ChatSuggestionItem {
  label?: React.ReactNode;
  value: string;
}

export interface ChatActionSpec {
  /** Stable id, used for dispose tracking and deduplication. */
  id: string;
  icon?: React.ReactElement;
  /** Either `render` or `onClick` (render wins if both supplied). */
  render?: (ctx: { data: unknown }) => React.ReactElement;
  onClick?: (ctx: { data: unknown }) => void;
}

export interface OverrideRecord {
  kind: string;
  field: string;
  pluginId: string;
  supersededPluginId?: string;
  detail?: string;
  timestamp: number;
}

export interface WelcomeRenderProps {
  greeting?: React.ReactNode;
  description?: React.ReactNode;
  avatar?: string | React.ReactNode;
  prompts?: ChatPromptItem[];
  onSubmit: (data: { query: string; fileList?: unknown[] }) => void;
}

/** Plugin-supplied welcome render: either a fn (receives SDK props) or a plain node. */
export type WelcomeRenderValue =
  | ((props: WelcomeRenderProps) => React.ReactElement)
  | React.ReactNode;

/** Opaque request/response data. Plugin authors can cast if they need strong typing. */
export type ChatRequestData = Record<string, unknown>;
export type ChatResponseData = Record<string, unknown>;

export type ChatRequestRenderFn = (ctx: {
  data: ChatRequestData;
  fallback: () => React.ReactElement;
}) => React.ReactNode;

export type ChatResponseRenderFn = (ctx: {
  data: ChatResponseData;
  isLast?: boolean;
  fallback: () => React.ReactElement;
}) => React.ReactNode;

export type ChatRequestSlotFn = (ctx: {
  data: ChatRequestData;
}) => React.ReactNode;
export type ChatResponseSlotFn = (ctx: {
  data: ChatResponseData;
  isLast?: boolean;
}) => React.ReactNode;

export interface QwenPawChatNamespace {
  welcome: {
    set(
      pluginId: string,
      partial: Partial<{
        greeting: Localized<React.ReactNode>;
        description: Localized<React.ReactNode>;
        avatar: Localized<string | React.ReactNode>;
        nick: Localized<string | React.ReactNode>;
        prompts: Localized<ChatPromptItem[]>;
      }>,
    ): Disposable;
    /** Whole-section replacement. Wins over set() fields. */
    render(pluginId: string, value: WelcomeRenderValue): Disposable;
  };
  theme: {
    set(
      pluginId: string,
      partial: Partial<{ colorPrimary: string }>,
    ): Disposable;
  };
  leftHeader: {
    set(
      pluginId: string,
      partial: Partial<{
        logo: Localized<string | React.ReactNode>;
        title: Localized<React.ReactNode>;
      }>,
    ): Disposable;
    /** Whole-section replacement. Wins over set() fields. */
    render(pluginId: string, node: React.ReactNode): Disposable;
  };
  rightHeader: {
    /** Append-only — host's default header controls (session/model/history) always render. */
    add(
      pluginId: string,
      node: React.ReactNode,
      opts?: { id?: string; order?: number },
    ): Disposable;
  };
  sender: {
    set(
      pluginId: string,
      partial: Partial<{
        placeholder: Localized<string>;
        disclaimer: Localized<React.ReactNode>;
      }>,
    ): Disposable;
    addPrefix(
      pluginId: string,
      node: React.ReactNode,
      opts?: { id?: string; order?: number },
    ): Disposable;
    addSuggestion(
      pluginId: string,
      item: { id?: string; items: Localized<ChatSuggestionItem[]> },
    ): Disposable;
  };
  actions: { add(pluginId: string, spec: ChatActionSpec): Disposable };
  requestActions: { add(pluginId: string, spec: ChatActionSpec): Disposable };
  request: {
    /** Whole-bubble replacement for the user request card. */
    render(pluginId: string, fn: ChatRequestRenderFn): Disposable;
    /** Insert a custom component above the user bubble. Returning null skips this bubble. */
    prepend(
      pluginId: string,
      fn: ChatRequestSlotFn,
      opts?: { id?: string; order?: number },
    ): Disposable;
    /** Insert a custom component below the user bubble. */
    append(
      pluginId: string,
      fn: ChatRequestSlotFn,
      opts?: { id?: string; order?: number },
    ): Disposable;
  };
  response: {
    /** Whole-bubble replacement for the assistant response card. */
    render(pluginId: string, fn: ChatResponseRenderFn): Disposable;
    /** Insert a custom component above the AI bubble. */
    prepend(
      pluginId: string,
      fn: ChatResponseSlotFn,
      opts?: { id?: string; order?: number },
    ): Disposable;
    /** Insert a custom component below the AI bubble. */
    append(
      pluginId: string,
      fn: ChatResponseSlotFn,
      opts?: { id?: string; order?: number },
    ): Disposable;
  };
  toolRender(
    pluginId: string,
    toolName: string,
    render: React.FC<Record<string, unknown>>,
  ): Disposable;
  card(
    pluginId: string,
    cardName: string,
    render: React.FC<Record<string, unknown>>,
  ): Disposable;
  /** Tear down every registration from this plugin. Useful for future hot-unload. */
  disposeAll(pluginId: string): void;
}

export interface QwenPawHostNamespace {
  // ── Shared dependencies (attached by hostExternals.ts) ────────────────────
  React: typeof React;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ReactDOM: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  antd: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  antdIcons: any;
  apiBaseUrl: string;
  getApiUrl(path: string): string;
  getApiToken(): string | null;

  // ── Hooks (call only inside plugin-supplied React components) ─────────────
  useTheme(): HostThemeMode;
  useLocale(): string;
  useSelectedAgent(): HostAgentInfo;
  useCurrentSession(): HostSessionInfo | null;

  // ── Imperative getters (safe outside React render) ────────────────────────
  getSelectedAgentId(): string;
  getCurrentSessionId(): string | null;

  /** Auth-aware fetch. Automatically injects `Authorization` and `X-Agent-Id`. */
  fetch(path: string, init?: RequestInit): Promise<Response>;

  // ── A2UI generative UI helpers (read-only surfaces in chat bubbles) ───────
  /** Renders an accumulated A2UI surface as React nodes (read-only by default). */
  A2uiRenderer: React.FC<A2uiRendererProps>;
  /** Folds one A2UI server→client message into a surface, returning a new one. */
  applyA2uiMessage(surface: A2uiSurface, msg: A2uiMessage): A2uiSurface;
  /** Creates a fresh, empty surface for the given id. */
  emptySurface(surfaceId: string): A2uiSurface;
}

export interface QwenPawAuditNamespace {
  overrides(): OverrideRecord[];
}

export interface PluginRouteDeclaration {
  path: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  component: React.ComponentType<any>;
  label: string;
  icon?: string;
  priority?: number;
}

export interface QwenPawWindowNamespace {
  host: QwenPawHostNamespace;
  chat: QwenPawChatNamespace;
  audit: QwenPawAuditNamespace;
  modules: Record<string, Record<string, unknown>>;
  registerRoutes?(pluginId: string, routes: PluginRouteDeclaration[]): void;
  registerToolRender?(
    pluginId: string,
    renderers: Record<string, React.FC<Record<string, unknown>>>,
  ): void;
}

// Plugin projects: uncomment this in your own qwenpaw-host.d.ts to type
// `window.QwenPaw.*` accesses in plugin code.
//
// declare global {
//   interface Window {
//     QwenPaw: QwenPawWindowNamespace;
//   }
// }

export {};
