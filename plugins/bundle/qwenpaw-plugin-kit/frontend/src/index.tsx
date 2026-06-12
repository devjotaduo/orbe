import type * as ReactNS from "react";

const pluginId = "qwenpaw-plugin-kit";
const host = window.QwenPaw?.host;
const React: typeof ReactNS = host.React;
const antd = host.antd;

function localText(locale: string, pt: string, en: string): string {
  return locale.toLowerCase().startsWith("pt") ? pt : en;
}

function getApiUrl(path: string): string {
  return host.getApiUrl ? host.getApiUrl(path) : `/api${path}`;
}

function PluginKitPage() {
  const locale = host.useLocale ? host.useLocale() : "pt-BR";
  const [data, setData] = React.useState<{
    loading: boolean;
    items: { id: string; name: string; description: string }[];
    error: string;
  }>({ loading: true, items: [], error: "" });

  React.useEffect(() => {
    let cancelled = false;
    fetch(getApiUrl("/plugin-kit/elements"))
      .then((response) => {
        if (!response.ok) throw new Error(String(response.status));
        return response.json();
      })
      .then((payload) => {
        if (!cancelled) {
          setData({ loading: false, items: payload.items || [], error: "" });
        }
      })
      .catch((error) => {
        if (!cancelled) {
          setData({ loading: false, items: [], error: String(error) });
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const title = localText(locale, "Kit de Plugin", "Plugin Kit");
  const intro = localText(
    locale,
    "Exemplo basico com backend, hooks, tool, router e extensoes frontend.",
    "Basic example with backend, hooks, tool, router, and frontend extensions.",
  );

  const { Card, List, Typography, Alert, Spin } = antd;

  return React.createElement(
    "div",
    { style: { maxWidth: 880, margin: "24px auto" } },
    React.createElement(
      Card,
      null,
      React.createElement(Typography.Title, { level: 3 }, title),
      React.createElement(Typography.Paragraph, null, intro),
      data.error
        ? React.createElement(Alert, {
            type: "error",
            message: data.error,
            showIcon: true,
          })
        : data.loading
          ? React.createElement(Spin, null)
          : React.createElement(List, {
              dataSource: data.items,
              renderItem: (item: {
                id: string;
                name: string;
                description: string;
              }) =>
                React.createElement(
                  List.Item,
                  { key: item.id },
                  React.createElement(List.Item.Meta, {
                    title: item.name,
                    description: item.description,
                  }),
                ),
            }),
    ),
  );
}

function setup(): void {
  if (window.QwenPaw.route?.add) {
    window.QwenPaw.route.add(pluginId, {
      id: "qwenpaw-plugin-kit.home",
      path: "/plugin/qwenpaw-plugin-kit",
      component: PluginKitPage,
    });
  } else if (window.QwenPaw.registerRoutes) {
    window.QwenPaw.registerRoutes(pluginId, [
      {
        path: "/plugin/qwenpaw-plugin-kit",
        component: PluginKitPage,
        label: "Plugin Kit",
        icon: "🧩",
        priority: 60,
      },
    ]);
  }

  window.QwenPaw.menu?.add?.(pluginId, {
    id: "qwenpaw-plugin-kit.menu",
    label: "Plugin Kit",
    icon: "🧩",
    route: "qwenpaw-plugin-kit.home",
    location: "primary.settings",
    order: 60,
  });

  window.QwenPaw.slot?.fill?.(pluginId, "content.statusBar", () =>
    React.createElement(
      "span",
      { style: { fontSize: 12, opacity: 0.72 } },
      "Plugin Kit ativo",
    ),
  );
}

setup();
