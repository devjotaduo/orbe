import { describe, it, expect } from "vitest";
import {
  isBind,
  joinBase,
  resolveBind,
  setPath,
  resolveProps,
} from "./binding";

const DATA = { proposed_team: [{ name: "Atendente", tasks: ["a", "b"] }] };

describe("binding", () => {
  it("isBind detects $bind objects", () => {
    expect(isBind({ $bind: "x" })).toBe(true);
    expect(isBind("x")).toBe(false);
    expect(isBind(null)).toBe(false);
  });

  it("joinBase joins base path and relative path", () => {
    expect(joinBase("proposed_team/0", "name")).toBe("proposed_team/0/name");
    expect(joinBase(undefined, "name")).toBe("name");
  });

  it('joinBase treats "." as the item itself (string-array binds)', () => {
    expect(joinBase("proposed_team/0/tasks/1", ".")).toBe(
      "proposed_team/0/tasks/1",
    );
    expect(joinBase(undefined, ".")).toBe("");
  });

  it("resolveBind walks json-pointer-like paths", () => {
    expect(resolveBind(DATA, "proposed_team/0/name")).toBe("Atendente");
    expect(resolveBind(DATA, "proposed_team/0/tasks/1")).toBe("b");
  });

  it("resolveBind returns undefined on missing path", () => {
    expect(resolveBind(DATA, "proposed_team/9/name")).toBeUndefined();
  });

  it("setPath writes immutably", () => {
    const next = setPath(DATA, "proposed_team/0/name", "Novo");
    expect(next.proposed_team[0].name).toBe("Novo");
    expect(DATA.proposed_team[0].name).toBe("Atendente");
    expect(next).not.toBe(DATA);
  });

  it("setPath keeps array identity semantics (copies, same length)", () => {
    const next = setPath(DATA, "proposed_team/0/tasks/0", "z");
    expect(next.proposed_team[0].tasks).toEqual(["z", "b"]);
    expect(DATA.proposed_team[0].tasks).toEqual(["a", "b"]);
  });

  it("resolveProps resolves $bind values with basePath", () => {
    const props = { label: "Nome", value: { $bind: "name" } };
    const out = resolveProps(props, DATA, "proposed_team/0");
    expect(out.value).toBe("Atendente");
    expect(out.label).toBe("Nome");
  });
});
