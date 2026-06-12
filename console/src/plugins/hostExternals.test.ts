import { describe, it, expect } from "vitest";
import { installHostExternals } from "./hostExternals";

describe("host A2UI surface", () => {
  it("exposes A2uiRenderer + applyA2uiMessage + emptySurface on host", () => {
    installHostExternals();
    const host = (
      window as unknown as {
        QwenPaw: { host: Record<string, unknown> };
      }
    ).QwenPaw.host;
    expect(typeof host.A2uiRenderer).toBe("function");
    expect(typeof host.applyA2uiMessage).toBe("function");
    expect(typeof host.emptySurface).toBe("function");
  });
});
