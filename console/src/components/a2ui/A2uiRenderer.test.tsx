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

const TAG_MSGS: A2uiMessage[] = [
  { messageType: "createSurface", surfaceId: "bp", root: "root" },
  {
    messageType: "updateComponents",
    surfaceId: "bp",
    components: [
      { id: "root", type: "Column", properties: {}, children: ["n", "t"] },
      {
        id: "n",
        type: "TextInput",
        properties: { bind: "proposed_team/0/name", label: "Nome" },
        children: [],
      },
      {
        id: "t",
        type: "Tag",
        properties: { text: { $bind: "proposed_team/0/tag" } },
        children: [],
      },
    ],
  },
  {
    messageType: "updateDataModel",
    surfaceId: "bp",
    data: { proposed_team: [{ name: "Atendente", tag: "WhatsApp" }] },
  },
];

describe("A2uiRenderer (read-only components)", () => {
  function buildTagSurface() {
    let s = emptySurface("bp");
    for (const m of TAG_MSGS) s = applyA2uiMessage(s, m);
    return s;
  }

  it("Tag resolves bound text but stays non-editable", () => {
    render(<A2uiRenderer surface={buildTagSurface()} />);
    const tag = screen.getByText("WhatsApp");
    // The tag must never become a form control, even with a bound value.
    expect(["INPUT", "TEXTAREA"]).not.toContain(tag.tagName);
    expect(tag.closest("input,textarea")).toBeNull();
    // Only the explicit TextInput is editable in this surface.
    expect(screen.getAllByRole("textbox")).toHaveLength(1);
    expect(screen.getByRole("textbox")).toBe(screen.getByLabelText("Nome"));
  });
});

const REPEAT_MSGS: A2uiMessage[] = [
  { messageType: "createSurface", surfaceId: "bp", root: "root" },
  {
    messageType: "updateComponents",
    surfaceId: "bp",
    components: [
      { id: "root", type: "Column", properties: {}, children: ["rep"] },
      {
        id: "rep",
        type: "Repeater",
        properties: { bind: "proposed_team", itemTemplate: "tpl" },
        children: [],
      },
      {
        id: "tpl",
        type: "TextInput",
        properties: { bind: "name", label: "Nome" },
        children: [],
      },
    ],
  },
  {
    messageType: "updateDataModel",
    surfaceId: "bp",
    data: { proposed_team: [{ name: "A1" }, { name: "A2" }] },
  },
];

function buildRepeatSurface(msgs: A2uiMessage[] = REPEAT_MSGS) {
  let s = emptySurface("bp");
  for (const m of msgs) s = applyA2uiMessage(s, m);
  return s;
}

describe("A2uiRenderer (Repeater)", () => {
  it("instantiates the template once per item with relative binds", () => {
    render(<A2uiRenderer surface={buildRepeatSurface()} />);
    expect(screen.getByDisplayValue("A1")).toBeTruthy();
    expect(screen.getByDisplayValue("A2")).toBeTruthy();
    expect(screen.getAllByRole("textbox")).toHaveLength(2);
  });

  it("editing inside a repeater writes to the right index", () => {
    const onDataChange = vi.fn();
    render(
      <A2uiRenderer surface={buildRepeatSurface()} onDataChange={onDataChange} />,
    );
    fireEvent.change(screen.getByDisplayValue("A2"), {
      target: { value: "A2-edit" },
    });
    const next = onDataChange.mock.calls[0][0] as {
      proposed_team: Array<{ name: string }>;
    };
    expect(next.proposed_team[1].name).toBe("A2-edit");
    expect(next.proposed_team[0].name).toBe("A1");
  });

  it('bind "." resolves to the item itself (string arrays)', () => {
    const msgs: A2uiMessage[] = [
      { messageType: "createSurface", surfaceId: "bp", root: "root" },
      {
        messageType: "updateComponents",
        surfaceId: "bp",
        components: [
          { id: "root", type: "Column", properties: {}, children: ["rep"] },
          {
            id: "rep",
            type: "Repeater",
            properties: { bind: "tasks", itemTemplate: "tpl" },
            children: [],
          },
          {
            id: "tpl",
            type: "TextInput",
            properties: { bind: ".", label: "Tarefa" },
            children: [],
          },
        ],
      },
      {
        messageType: "updateDataModel",
        surfaceId: "bp",
        data: { tasks: ["ligar", "responder"] },
      },
    ];
    const onDataChange = vi.fn();
    render(
      <A2uiRenderer
        surface={buildRepeatSurface(msgs)}
        onDataChange={onDataChange}
      />,
    );
    expect(screen.getByDisplayValue("ligar")).toBeTruthy();
    fireEvent.change(screen.getByDisplayValue("responder"), {
      target: { value: "responder rapido" },
    });
    const next = onDataChange.mock.calls[0][0] as { tasks: string[] };
    expect(next.tasks).toEqual(["ligar", "responder rapido"]);
  });

  it("indexFromRepeater injects the item index (path defaults to the array)", () => {
    const msgs: A2uiMessage[] = [
      { messageType: "createSurface", surfaceId: "bp", root: "root" },
      {
        messageType: "updateComponents",
        surfaceId: "bp",
        components: [
          { id: "root", type: "Column", properties: {}, children: ["rep"] },
          {
            id: "rep",
            type: "Repeater",
            properties: { bind: "proposed_team", itemTemplate: "tpl" },
            children: [],
          },
          { id: "tpl", type: "Row", properties: {}, children: ["del"] },
          {
            id: "del",
            type: "Button",
            properties: {
              text: "Remover",
              action: {
                name: "remove_agent",
                params: { indexFromRepeater: true },
              },
            },
            children: [],
          },
        ],
      },
      {
        messageType: "updateDataModel",
        surfaceId: "bp",
        data: { proposed_team: [{ name: "A1" }, { name: "A2" }] },
      },
    ];
    const onAction = vi.fn();
    render(
      <A2uiRenderer surface={buildRepeatSurface(msgs)} onAction={onAction} />,
    );
    fireEvent.click(screen.getAllByText("Remover")[1]);
    expect(onAction).toHaveBeenCalledWith(
      "remove_agent",
      expect.objectContaining({ index: 1, path: "proposed_team" }),
    );
  });

  it("pathFromBase absolutizes a relative params.path against the item base", () => {
    const msgs: A2uiMessage[] = [
      { messageType: "createSurface", surfaceId: "bp", root: "root" },
      {
        messageType: "updateComponents",
        surfaceId: "bp",
        components: [
          { id: "root", type: "Column", properties: {}, children: ["rep"] },
          {
            id: "rep",
            type: "Repeater",
            properties: { bind: "proposed_team", itemTemplate: "tpl" },
            children: [],
          },
          { id: "tpl", type: "Row", properties: {}, children: ["add"] },
          {
            id: "add",
            type: "Button",
            properties: {
              text: "+ Tarefa",
              action: {
                name: "add_item",
                params: { path: "tasks", pathFromBase: true },
              },
            },
            children: [],
          },
        ],
      },
      {
        messageType: "updateDataModel",
        surfaceId: "bp",
        data: { proposed_team: [{ name: "A1" }, { name: "A2" }] },
      },
    ];
    const onAction = vi.fn();
    render(
      <A2uiRenderer surface={buildRepeatSurface(msgs)} onAction={onAction} />,
    );
    fireEvent.click(screen.getAllByText("+ Tarefa")[1]);
    expect(onAction).toHaveBeenCalledWith(
      "add_item",
      expect.objectContaining({ path: "proposed_team/1/tasks" }),
    );
  });

  it("nested Repeater: the innermost repeater context wins for indexFromRepeater", () => {
    const msgs: A2uiMessage[] = [
      { messageType: "createSurface", surfaceId: "bp", root: "root" },
      {
        messageType: "updateComponents",
        surfaceId: "bp",
        components: [
          { id: "root", type: "Column", properties: {}, children: ["rep"] },
          {
            id: "rep",
            type: "Repeater",
            properties: { bind: "proposed_team", itemTemplate: "card" },
            children: [],
          },
          { id: "card", type: "Row", properties: {}, children: ["trep"] },
          {
            id: "trep",
            type: "Repeater",
            properties: { bind: "tasks", itemTemplate: "del" },
            children: [],
          },
          {
            id: "del",
            type: "Button",
            properties: {
              text: "Del",
              action: {
                name: "remove_item",
                params: { indexFromRepeater: true },
              },
            },
            children: [],
          },
        ],
      },
      {
        messageType: "updateDataModel",
        surfaceId: "bp",
        data: {
          proposed_team: [{ tasks: ["t1", "t2"] }, { tasks: ["x1"] }],
        },
      },
    ];
    const onAction = vi.fn();
    render(
      <A2uiRenderer surface={buildRepeatSurface(msgs)} onAction={onAction} />,
    );
    // Render order: agent0/t1, agent0/t2, agent1/x1.
    const buttons = screen.getAllByText("Del");
    expect(buttons).toHaveLength(3);

    // Agent 0, second task: the OUTER repeater would inject index 0 /
    // path "proposed_team" — the inner one must win with index 1 and the
    // item-scoped tasks array path.
    fireEvent.click(buttons[1]);
    expect(onAction).toHaveBeenLastCalledWith(
      "remove_item",
      expect.objectContaining({ index: 1, path: "proposed_team/0/tasks" }),
    );

    // Agent 1, first task: inner index resets to 0 under the second agent.
    fireEvent.click(buttons[2]);
    expect(onAction).toHaveBeenLastCalledWith(
      "remove_item",
      expect.objectContaining({ index: 0, path: "proposed_team/1/tasks" }),
    );
  });

  it("shows a visible fallback when the bound value is not an array", () => {
    const msgs: A2uiMessage[] = [
      REPEAT_MSGS[0],
      REPEAT_MSGS[1],
      {
        messageType: "updateDataModel",
        surfaceId: "bp",
        data: { proposed_team: "oops" },
      },
    ];
    const { container } = render(
      <A2uiRenderer surface={buildRepeatSurface(msgs)} />,
    );
    expect(container.textContent).toContain("Repeater");
  });

  it("shows a visible fallback when the itemTemplate id does not exist", () => {
    const msgs: A2uiMessage[] = [
      { messageType: "createSurface", surfaceId: "bp", root: "root" },
      {
        messageType: "updateComponents",
        surfaceId: "bp",
        components: [
          { id: "root", type: "Column", properties: {}, children: ["rep"] },
          {
            id: "rep",
            type: "Repeater",
            properties: { bind: "proposed_team", itemTemplate: "ghost" },
            children: [],
          },
        ],
      },
      {
        messageType: "updateDataModel",
        surfaceId: "bp",
        data: { proposed_team: [{ name: "A1" }] },
      },
    ];
    const { container } = render(
      <A2uiRenderer surface={buildRepeatSurface(msgs)} />,
    );
    expect(container.textContent).toContain("Repeater");
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
