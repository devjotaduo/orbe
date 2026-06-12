import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/config", () => ({
  getApiToken: () => "test-token",
  getApiUrl: (path: string) => `/api/${path.replace(/^\/+/, "")}`,
}));

import { loadAllPlugins } from "./usePluginLoader";

function jsonResponse(body: unknown): Response {
  return {
    ok: true,
    status: 200,
    json: async () => body,
    text: async () => JSON.stringify(body),
  } as Response;
}

function jsResponse(source: string): Response {
  return {
    ok: true,
    status: 200,
    text: async () => source,
  } as Response;
}

describe("usePluginLoader", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("fetches plugin bundles with no-store cache and auth headers", async () => {
    const fetchMock = vi.fn(async (url: string) => {
      if (url === "/api/frontend_plugin") {
        return jsonResponse([
          {
            id: "nexora-admin",
            name: "Nexora Admin",
            frontend_entry: "ui/dist/index.js",
          },
        ]);
      }
      return jsResponse("export {};");
    });
    vi.stubGlobal("fetch", fetchMock);
    vi.spyOn(URL, "createObjectURL").mockReturnValue(
      "data:text/javascript,export%20{}",
    );
    vi.spyOn(URL, "revokeObjectURL").mockImplementation(() => undefined);

    await expect(loadAllPlugins()).resolves.toEqual({
      loaded: 1,
      failed: [],
    });

    expect(fetchMock).toHaveBeenCalledWith("/api/frontend_plugin", {
      headers: { Authorization: "Bearer test-token" },
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/frontend_plugin/nexora-admin/files/ui/dist/index.js",
      {
        cache: "no-store",
        headers: { Authorization: "Bearer test-token" },
      },
    );
  });
});
