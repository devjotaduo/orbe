/**
 * nexoraAdminPlugin.test.tsx — covers the nexora-admin plugin bundle:
 *
 *  - with `audit.view`: registers route "/nexora/audit" AND a sidebar menu
 *    item in primary.settings whose `visible()` mirrors the permission set.
 *  - without `audit.view`: route is still registered (backend enforces
 *    RBAC) but NO menu item is added.
 *  - the Audit page renders via host React/antd and fetches
 *    `/nexora/audit` through the auth-aware host.fetch.
 *
 * The plugin file lives outside console/src; it calls install() on import
 * and registers through window.QwenPaw.{route,menu}, pulling React/antd
 * from window.QwenPaw.host — we stub the host and import the bundle.
 */
import { describe, it, expect, beforeEach, vi } from "vitest";
import React from "react";
import * as antd from "antd";
import { render, screen, waitFor } from "@testing-library/react";

// Vite resolves a *literal* dynamic-import string relative to this file.
const importBundle = () =>
  import("../../../plugins/bundle/nexora-admin/ui/src/index.ts");

type AnyRec = Record<string, unknown>;

interface MenuItemStub {
  id: string;
  location?: string;
  parentId?: string;
  route?: string;
  visible?: () => boolean;
}

interface RouteStub {
  id: string;
  path: string;
  component: React.ComponentType;
}

function jsonResponse(body: unknown, ok = true): Response {
  return {
    ok,
    status: ok ? 200 : 403,
    json: async () => body,
  } as unknown as Response;
}

function stubQwenPaw(opts: {
  permissions: string[] | null; // null → /auth/me fails
  events?: AnyRec[];
}) {
  const routeAdd = vi.fn(() => ({ dispose: vi.fn() }));
  const menuAdd = vi.fn(() => ({ dispose: vi.fn() }));
  const hostFetch = vi.fn(async (path: string) => {
    if (path.startsWith("/auth/me")) {
      if (opts.permissions === null) return jsonResponse({}, false);
      return jsonResponse({
        username: "admin",
        roles: ["admin"],
        permissions: opts.permissions,
      });
    }
    if (path.startsWith("/nexora/audit")) {
      return jsonResponse(opts.events ?? []);
    }
    return jsonResponse({}, false);
  });

  (window as unknown as AnyRec).QwenPaw = {
    host: {
      React,
      antd,
      antdIcons: {},
      fetch: hostFetch,
      useLocale: () => "pt-BR",
    },
    route: { add: routeAdd },
    menu: { add: menuAdd },
  };

  return { routeAdd, menuAdd, hostFetch };
}

describe("nexora-admin plugin", () => {
  beforeEach(() => {
    vi.resetModules();
    delete (window as unknown as AnyRec).QwenPaw;
  });

  it("registers /nexora/audit route and menu item when user has audit.view", async () => {
    const { routeAdd, menuAdd } = stubQwenPaw({
      permissions: ["audit.view", "users.view"],
    });

    await importBundle();
    await waitFor(() => expect(menuAdd).toHaveBeenCalledTimes(1));

    expect(routeAdd).toHaveBeenCalledTimes(1);
    const [routePluginId, route] = routeAdd.mock.calls[0] as unknown as [
      string,
      RouteStub,
    ];
    expect(routePluginId).toBe("nexora-admin");
    expect(route.id).toBe("nexora-admin.audit");
    expect(route.path).toBe("/nexora/audit");
    expect(typeof route.component).toBe("function");

    const [menuPluginId, item] = menuAdd.mock.calls[0] as unknown as [
      string,
      MenuItemStub,
    ];
    expect(menuPluginId).toBe("nexora-admin");
    expect(item.id).toBe("nexora-admin.audit");
    expect(item.location).toBe("primary.settings");
    expect(item.route).toBe("nexora-admin.audit");
    expect(item.visible?.()).toBe(true);
  });

  it("menu visible() flips to false when the permission set loses audit.view", async () => {
    const { menuAdd } = stubQwenPaw({ permissions: ["audit.view"] });

    const mod = await importBundle();
    await waitFor(() => expect(menuAdd).toHaveBeenCalledTimes(1));

    const [, item] = menuAdd.mock.calls[0] as unknown as [string, MenuItemStub];
    expect(item.visible?.()).toBe(true);

    (
      mod as AnyRec & { state: { permissions: Set<string> } }
    ).state.permissions = new Set();
    expect(item.visible?.()).toBe(false);
  });

  it("does NOT add a menu item without audit.view (route still registered)", async () => {
    const { routeAdd, menuAdd } = stubQwenPaw({ permissions: [] });

    await importBundle();
    await waitFor(() => expect(routeAdd).toHaveBeenCalledTimes(1));
    // Give the async permission fetch a tick to settle.
    await new Promise((r) => setTimeout(r, 0));

    expect(menuAdd).not.toHaveBeenCalled();
  });

  it("does NOT add a menu item when /auth/me fails (auth disabled / no extension)", async () => {
    const { routeAdd, menuAdd } = stubQwenPaw({ permissions: null });

    await importBundle();
    await waitFor(() => expect(routeAdd).toHaveBeenCalledTimes(1));
    await new Promise((r) => setTimeout(r, 0));

    expect(menuAdd).not.toHaveBeenCalled();
  });

  it("Audit page fetches /nexora/audit via host.fetch and renders events", async () => {
    const { routeAdd, hostFetch } = stubQwenPaw({
      permissions: ["audit.view"],
      events: [
        {
          id: "evt-1",
          timestamp: 1760000000,
          actor: "alice",
          action: "auth.login",
          status: "success",
          resource_type: "auth",
          resource_id: "user:alice",
          ip: "10.0.0.1",
          detail: { roles: ["admin"] },
        },
      ],
    });

    await importBundle();
    await waitFor(() => expect(routeAdd).toHaveBeenCalledTimes(1));

    const [, route] = routeAdd.mock.calls[0] as unknown as [string, RouteStub];
    const Page = route.component;
    render(<Page />);

    await waitFor(() =>
      expect(
        hostFetch.mock.calls.some((c) =>
          String(c[0]).startsWith("/nexora/audit?"),
        ),
      ).toBe(true),
    );
    await waitFor(() => expect(screen.getByText("alice")).toBeInTheDocument());
    expect(screen.getByText("10.0.0.1")).toBeInTheDocument();
  });
});
