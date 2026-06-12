import type * as React from "react";

declare global {
  interface Window {
    QwenPaw: {
      host: {
        React: typeof React;
        antd: any;
        getApiUrl?: (path: string) => string;
        useLocale?: () => string;
      };
      menu?: {
        add?: (pluginId: string, item: Record<string, unknown>) => unknown;
      };
      route?: {
        add?: (pluginId: string, route: Record<string, unknown>) => unknown;
      };
      slot?: {
        fill?: (
          pluginId: string,
          name: string,
          render: (...args: unknown[]) => React.ReactNode,
        ) => unknown;
      };
      registerRoutes?: (
        pluginId: string,
        routes: Record<string, unknown>[],
      ) => unknown;
    };
  }
}

export {};
