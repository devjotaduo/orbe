import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
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
