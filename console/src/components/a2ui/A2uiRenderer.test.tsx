import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { applyA2uiMessage, emptySurface } from "./surfaceReducer";
import { A2uiRenderer } from "./A2uiRenderer";
import type { A2uiMessage } from "../../api/types/a2ui";

const MSGS: A2uiMessage[] = [
  { messageType: "createSurface", surfaceId: "bp", root: "root" },
  {
    messageType: "updateComponents",
    surfaceId: "bp",
    components: [
      { id: "root", type: "Column", properties: {}, children: ["h", "u"] },
      {
        id: "h",
        type: "Heading",
        properties: { text: "Time proposto" },
        children: [],
      },
      { id: "u", type: "Unknownz", properties: { text: "x" }, children: [] },
    ],
  },
];

function buildSurface() {
  let s = emptySurface("bp");
  for (const m of MSGS) s = applyA2uiMessage(s, m);
  return s;
}

describe("A2uiRenderer", () => {
  it("renders a heading from the adjacency list", () => {
    render(<A2uiRenderer surface={buildSurface()} />);
    expect(screen.getByText("Time proposto")).toBeTruthy();
  });

  it("shows a visible fallback for unknown component types", () => {
    render(<A2uiRenderer surface={buildSurface()} />);
    expect(screen.getByText(/Unknownz/)).toBeTruthy();
  });
});

const EDIT_MSGS: A2uiMessage[] = [
  { messageType: "createSurface", surfaceId: "bp", root: "root" },
  {
    messageType: "updateComponents",
    surfaceId: "bp",
    components: [
      { id: "root", type: "Column", properties: {}, children: ["n", "ok"] },
      {
        id: "n",
        type: "TextInput",
        properties: { bind: "proposed_team/0/name", label: "Nome" },
        children: [],
      },
      {
        id: "ok",
        type: "Button",
        properties: { text: "Aprovar", action: { name: "approve_team" } },
        children: [],
      },
    ],
  },
  {
    messageType: "updateDataModel",
    surfaceId: "bp",
    data: { proposed_team: [{ name: "Atendente" }] },
  },
];

function buildEditSurface() {
  let s = emptySurface("bp");
  for (const m of EDIT_MSGS) s = applyA2uiMessage(s, m);
  return s;
}

describe("A2uiRenderer (binding-aware)", () => {
  it("TextInput renders bound value and writes back via onDataChange", () => {
    const onDataChange = vi.fn();
    render(
      <A2uiRenderer surface={buildEditSurface()} onDataChange={onDataChange} />,
    );
    const input = screen.getByDisplayValue("Atendente");
    fireEvent.change(input, { target: { value: "Vendedor" } });
    expect(onDataChange).toHaveBeenCalled();
    const next = onDataChange.mock.calls[0][0] as {
      proposed_team: Array<{ name: string }>;
    };
    expect(next.proposed_team[0].name).toBe("Vendedor");
  });

  it("TextInput is labelled for accessibility", () => {
    render(<A2uiRenderer surface={buildEditSurface()} />);
    expect(screen.getByLabelText("Nome")).toBeTruthy();
  });

  it("Button with action dispatches onAction", () => {
    const onAction = vi.fn();
    render(<A2uiRenderer surface={buildEditSurface()} onAction={onAction} />);
    fireEvent.click(screen.getByText("Aprovar"));
    expect(onAction).toHaveBeenCalledWith("approve_team", undefined);
  });

  it("explicit data prop overrides surface.data", () => {
    render(
      <A2uiRenderer
        surface={buildEditSurface()}
        data={{ proposed_team: [{ name: "Editado" }] }}
      />,
    );
    expect(screen.getByDisplayValue("Editado")).toBeTruthy();
  });
});

describe("surfaceReducer", () => {
  it("createSurface sets the root", () => {
    const s = applyA2uiMessage(emptySurface("bp"), MSGS[0]);
    expect(s.root).toBe("root");
  });

  it("updateComponents indexes components by id", () => {
    const s = buildSurface();
    expect(Object.keys(s.components).sort()).toEqual(["h", "root", "u"]);
  });

  it("deleteSurface resets the surface", () => {
    let s = buildSurface();
    s = applyA2uiMessage(s, { messageType: "deleteSurface", surfaceId: "bp" });
    expect(s.root).toBe("");
    expect(Object.keys(s.components)).toHaveLength(0);
  });
});
