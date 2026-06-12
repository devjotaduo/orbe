import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { screen, waitFor, fireEvent, act } from "@testing-library/react";
import { renderWithProviders } from "@/test/common_setup";
import type { AguiEvent } from "../../api/types/agui";
import DiscoveryPage from "./index";

const { mockStreamTurn, mockAction } = vi.hoisted(() => ({
  mockStreamTurn: vi.fn(),
  mockAction: vi.fn(),
}));

vi.mock("../../api/modules/discovery", () => ({
  discoveryApi: { streamTurn: mockStreamTurn, action: mockAction },
}));

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (k: string) => k }),
}));

vi.mock("@/components/PageHeader", () => ({
  PageHeader: () => null,
}));

/**
 * Make streamTurn drive `onEvent` synchronously with a scripted list of AG-UI
 * events, then resolve — simulating one SSE turn without a real network stream.
 */
function scriptTurn(events: AguiEvent[]) {
  mockStreamTurn.mockImplementationOnce(
    async (
      _sessionId: string,
      _message: string | null,
      onEvent: (ev: AguiEvent) => void,
    ) => {
      for (const ev of events) onEvent(ev);
    },
  );
}

const AGENT_HELLO: AguiEvent[] = [
  { type: "RUN_STARTED", threadId: "t", runId: "r" },
  { type: "TEXT_MESSAGE_CONTENT", messageId: "m1", delta: "Qual o " },
  { type: "TEXT_MESSAGE_CONTENT", messageId: "m1", delta: "objetivo?" },
  { type: "STATE_SNAPSHOT", snapshot: { step: "intro" } },
  { type: "RUN_FINISHED", threadId: "t", runId: "r" },
];

// Final turn: agent text + a CUSTOM a2ui surface (createSurface + components).
const BLUEPRINT_TURN: AguiEvent[] = [
  { type: "TEXT_MESSAGE_CONTENT", messageId: "m2", delta: "Aqui esta seu time." },
  {
    type: "CUSTOM",
    name: "a2ui",
    value: { messageType: "createSurface", surfaceId: "blueprint", root: "root" },
  },
  {
    type: "CUSTOM",
    name: "a2ui",
    value: {
      messageType: "updateComponents",
      surfaceId: "blueprint",
      components: [
        { id: "root", type: "Column", properties: {}, children: ["h"] },
        {
          id: "h",
          type: "Heading",
          properties: { text: "Time proposto" },
          children: [],
        },
      ],
    },
  },
  { type: "RUN_FINISHED", threadId: "t", runId: "r" },
];

/** Final turn delivering an editable surface (bound input + approve button). */
const EDITABLE_TURN: AguiEvent[] = [
  {
    type: "CUSTOM",
    name: "a2ui",
    value: { messageType: "createSurface", surfaceId: "blueprint", root: "root" },
  },
  {
    type: "CUSTOM",
    name: "a2ui",
    value: {
      messageType: "updateComponents",
      surfaceId: "blueprint",
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
          properties: {
            text: "Aprovar time",
            variant: "primary",
            action: { name: "approve_team" },
          },
          children: [],
        },
      ],
    },
  },
  {
    type: "CUSTOM",
    name: "a2ui",
    value: {
      messageType: "updateDataModel",
      surfaceId: "blueprint",
      data: { proposed_team: [{ name: "Atendente" }] },
    },
  },
  { type: "RUN_FINISHED", threadId: "t", runId: "r" },
];

/**
 * Final turn with structural buttons (Fase 2): a Repeater over proposed_team
 * plus add/remove/move agent buttons and add/remove item buttons for the
 * first agent's tasks. All of them must mutate the LOCAL data model only.
 */
const STRUCTURAL_TURN: AguiEvent[] = [
  {
    type: "CUSTOM",
    name: "a2ui",
    value: { messageType: "createSurface", surfaceId: "blueprint", root: "root" },
  },
  {
    type: "CUSTOM",
    name: "a2ui",
    value: {
      messageType: "updateComponents",
      surfaceId: "blueprint",
      components: [
        {
          id: "root",
          type: "Column",
          properties: {},
          children: [
            "rep",
            "trep",
            "add",
            "rm",
            "rm-noidx",
            "mv",
            "mv0",
            "mv-stale",
            "addi",
            "rmi",
            "rmi-noidx",
          ],
        },
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
        {
          id: "trep",
          type: "Repeater",
          properties: { bind: "proposed_team/0/tasks", itemTemplate: "ttpl" },
          children: [],
        },
        {
          id: "ttpl",
          type: "TextInput",
          properties: { bind: ".", label: "Tarefa" },
          children: [],
        },
        {
          id: "add",
          type: "Button",
          properties: { text: "Add agente", action: { name: "add_agent" } },
          children: [],
        },
        {
          id: "rm",
          type: "Button",
          properties: {
            text: "Remover 0",
            action: {
              name: "remove_agent",
              params: { path: "proposed_team", index: 0 },
            },
          },
          children: [],
        },
        {
          // Defensive case: a remove_agent action whose params carry no index
          // (e.g. a malformed surface) must not delete anything.
          id: "rm-noidx",
          type: "Button",
          properties: {
            text: "Remover sem indice",
            action: {
              name: "remove_agent",
              params: { path: "proposed_team" },
            },
          },
          children: [],
        },
        {
          id: "mv",
          type: "Button",
          properties: {
            text: "Subir 1",
            action: {
              name: "move_agent",
              params: { path: "proposed_team", index: 1, dir: -1 },
            },
          },
          children: [],
        },
        {
          id: "mv0",
          type: "Button",
          properties: {
            text: "Subir 0",
            action: {
              name: "move_agent",
              params: { path: "proposed_team", index: 0, dir: -1 },
            },
          },
          children: [],
        },
        {
          // Defensive case: a stale index pointing one past the end (item was
          // already removed elsewhere) combined with dir -1 must be a no-op,
          // never a swap with a hole past the array boundary.
          id: "mv-stale",
          type: "Button",
          properties: {
            text: "Subir 2 (stale)",
            action: {
              name: "move_agent",
              params: { path: "proposed_team", index: 2, dir: -1 },
            },
          },
          children: [],
        },
        {
          id: "addi",
          type: "Button",
          properties: {
            text: "+ Tarefa",
            action: {
              name: "add_item",
              params: { path: "proposed_team/0/tasks" },
            },
          },
          children: [],
        },
        {
          id: "rmi",
          type: "Button",
          properties: {
            text: "- Tarefa",
            action: {
              name: "remove_item",
              params: { path: "proposed_team/0/tasks", index: 0 },
            },
          },
          children: [],
        },
        {
          // Defensive case: remove_item without an index must not delete
          // anything either.
          id: "rmi-noidx",
          type: "Button",
          properties: {
            text: "- Tarefa sem indice",
            action: {
              name: "remove_item",
              params: { path: "proposed_team/0/tasks" },
            },
          },
          children: [],
        },
      ],
    },
  },
  {
    type: "CUSTOM",
    name: "a2ui",
    value: {
      messageType: "updateDataModel",
      surfaceId: "blueprint",
      data: {
        proposed_team: [
          { name: "A1", tasks: ["t1"] },
          { name: "A2", tasks: [] },
        ],
      },
    },
  },
  { type: "RUN_FINISHED", threadId: "t", runId: "r" },
];

/** Make discoveryApi.action drive `onEvent` with a scripted event list. */
function scriptAction(events: AguiEvent[]) {
  mockAction.mockImplementationOnce(
    async (
      _sessionId: string,
      _name: string,
      _data: Record<string, unknown>,
      onEvent: (ev: AguiEvent) => void,
    ) => {
      for (const ev of events) onEvent(ev);
    },
  );
}

describe("DiscoveryPage", () => {
  beforeEach(() => {
    mockStreamTurn.mockReset();
    mockAction.mockReset();
  });
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders the start screen with no transcript before starting", () => {
    renderWithProviders(<DiscoveryPage />);
    expect(screen.getByText("discovery.start")).toBeTruthy();
    expect(mockStreamTurn).not.toHaveBeenCalled();
  });

  it("clicking Start streams the agent turn and renders its transcript", async () => {
    scriptTurn(AGENT_HELLO);
    renderWithProviders(<DiscoveryPage />);

    fireEvent.click(screen.getByText("discovery.start"));

    await waitFor(() =>
      expect(screen.getByText(/Qual o objetivo\?/)).toBeTruthy(),
    );
    expect(mockStreamTurn).toHaveBeenCalledWith(
      expect.any(String),
      null,
      expect.any(Function),
      expect.any(AbortSignal),
    );
  });

  it("submitting an answer appends the user turn before the agent reply", async () => {
    scriptTurn(AGENT_HELLO);
    renderWithProviders(<DiscoveryPage />);
    fireEvent.click(screen.getByText("discovery.start"));
    await waitFor(() =>
      expect(screen.getByText(/Qual o objetivo\?/)).toBeTruthy(),
    );

    scriptTurn([
      { type: "TEXT_MESSAGE_CONTENT", messageId: "m3", delta: "Entendi." },
      { type: "RUN_FINISHED", threadId: "t", runId: "r" },
    ]);

    const input = screen.getByLabelText("discovery.answerPlaceholder");
    fireEvent.change(input, { target: { value: "vendas" } });
    fireEvent.click(screen.getByText("discovery.send"));

    // User turn appears immediately (optimistic), agent reply after stream.
    await waitFor(() => expect(screen.getByText(/vendas/)).toBeTruthy());
    await waitFor(() => expect(screen.getByText(/Entendi\./)).toBeTruthy());

    // Second streamTurn was called with the typed message.
    expect(mockStreamTurn).toHaveBeenLastCalledWith(
      expect.any(String),
      "vendas",
      expect.any(Function),
      expect.any(AbortSignal),
    );
  });

  it("a CUSTOM a2ui turn renders the surface and flips to the completed/Start Over state", async () => {
    scriptTurn(BLUEPRINT_TURN);
    renderWithProviders(<DiscoveryPage />);

    fireEvent.click(screen.getByText("discovery.start"));

    // The A2UI surface is rendered (Heading from the adjacency list).
    await waitFor(() => expect(screen.getByText("Time proposto")).toBeTruthy());
    // Completed state: Start Over button shown, composer/send hidden.
    expect(screen.getByText("discovery.restart")).toBeTruthy();
    expect(screen.queryByText("discovery.send")).toBeNull();
  });

  it("Start Over resets back to the intro screen", async () => {
    scriptTurn(BLUEPRINT_TURN);
    renderWithProviders(<DiscoveryPage />);
    fireEvent.click(screen.getByText("discovery.start"));
    await waitFor(() => expect(screen.getByText("discovery.restart")).toBeTruthy());

    fireEvent.click(screen.getByText("discovery.restart"));

    await waitFor(() => expect(screen.getByText("discovery.start")).toBeTruthy());
    expect(screen.queryByText("Time proposto")).toBeNull();
  });

  it("editing a bound field and approving sends the edited data model", async () => {
    scriptTurn(EDITABLE_TURN);
    scriptAction([{ type: "RUN_FINISHED", threadId: "t", runId: "r" }]);
    renderWithProviders(<DiscoveryPage />);

    fireEvent.click(screen.getByText("discovery.start"));
    await waitFor(() =>
      expect(screen.getByDisplayValue("Atendente")).toBeTruthy(),
    );

    fireEvent.change(screen.getByDisplayValue("Atendente"), {
      target: { value: "Vendedor" },
    });
    fireEvent.click(screen.getByText("Aprovar time"));

    await waitFor(() =>
      expect(screen.getByText("discovery.approvedTitle")).toBeTruthy(),
    );
    expect(mockAction).toHaveBeenCalledWith(
      expect.any(String),
      "approve_team",
      { proposed_team: [{ name: "Vendedor" }] },
      expect.any(Function),
      expect.any(AbortSignal),
    );
  });

  it("a RUN_ERROR on approve shows an alert and preserves the edits", async () => {
    scriptTurn(EDITABLE_TURN);
    scriptAction([
      { type: "RUN_ERROR", message: "blueprint invalido", code: "E422" },
      { type: "RUN_FINISHED", threadId: "t", runId: "r" },
    ]);
    renderWithProviders(<DiscoveryPage />);

    fireEvent.click(screen.getByText("discovery.start"));
    await waitFor(() =>
      expect(screen.getByDisplayValue("Atendente")).toBeTruthy(),
    );

    fireEvent.change(screen.getByDisplayValue("Atendente"), {
      target: { value: "Vendedor" },
    });
    fireEvent.click(screen.getByText("Aprovar time"));

    await waitFor(() =>
      expect(screen.getByText(/blueprint invalido/)).toBeTruthy(),
    );
    // Not approved, and the edit is still in the input for a retry.
    expect(screen.queryByText("discovery.approvedTitle")).toBeNull();
    expect(screen.getByDisplayValue("Vendedor")).toBeTruthy();
  });

  it("restart aborts an in-flight approve; its late resolution cannot approve the next session", async () => {
    scriptTurn(EDITABLE_TURN);
    let resolveAction!: () => void;
    let actionSignal: AbortSignal | undefined;
    mockAction.mockImplementationOnce(
      async (
        _sessionId: string,
        _name: string,
        _data: Record<string, unknown>,
        _onEvent: (ev: AguiEvent) => void,
        signal?: AbortSignal,
      ) => {
        actionSignal = signal;
        await new Promise<void>((res) => {
          resolveAction = res;
        });
      },
    );
    renderWithProviders(<DiscoveryPage />);

    fireEvent.click(screen.getByText("discovery.start"));
    await waitFor(() =>
      expect(screen.getByDisplayValue("Atendente")).toBeTruthy(),
    );
    fireEvent.click(screen.getByText("Aprovar time"));
    await waitFor(() => expect(mockAction).toHaveBeenCalled());

    // Restart while the approve request is still in flight.
    fireEvent.click(screen.getByText("discovery.restart"));
    expect(actionSignal?.aborted).toBe(true);

    // The stale promise resolves only now; with the abort guard it must not
    // flip `approved` for the session started next.
    await act(async () => {
      resolveAction();
    });

    scriptTurn(EDITABLE_TURN);
    fireEvent.click(screen.getByText("discovery.start"));
    await waitFor(() =>
      expect(screen.getByDisplayValue("Atendente")).toBeTruthy(),
    );
    expect(screen.queryByText("discovery.approvedTitle")).toBeNull();
  });

  describe("structural actions (local, no backend)", () => {
    async function renderStructural() {
      scriptTurn(STRUCTURAL_TURN);
      renderWithProviders(<DiscoveryPage />);
      fireEvent.click(screen.getByText("discovery.start"));
      await waitFor(() => expect(screen.getByDisplayValue("A1")).toBeTruthy());
    }

    it("add_agent appends a default agent locally", async () => {
      await renderStructural();
      fireEvent.click(screen.getByText("Add agente"));
      await waitFor(() =>
        expect(screen.getByDisplayValue("Novo agente")).toBeTruthy(),
      );
      expect(screen.getAllByLabelText("Nome")).toHaveLength(3);
      expect(mockAction).not.toHaveBeenCalled();
    });

    it("remove_agent removes the agent at the given index locally", async () => {
      await renderStructural();
      fireEvent.click(screen.getByText("Remover 0"));
      await waitFor(() =>
        expect(screen.queryByDisplayValue("A1")).toBeNull(),
      );
      expect(screen.getByDisplayValue("A2")).toBeTruthy();
      expect(mockAction).not.toHaveBeenCalled();
    });

    it("move_agent swaps neighbours locally", async () => {
      await renderStructural();
      fireEvent.click(screen.getByText("Subir 1"));
      await waitFor(() => {
        const names = screen
          .getAllByLabelText("Nome")
          .map((el) => (el as HTMLInputElement).value);
        expect(names).toEqual(["A2", "A1"]);
      });
      expect(mockAction).not.toHaveBeenCalled();
    });

    it("move_agent out of bounds is a no-op", async () => {
      await renderStructural();
      fireEvent.click(screen.getByText("Subir 0"));
      const names = screen
        .getAllByLabelText("Nome")
        .map((el) => (el as HTMLInputElement).value);
      expect(names).toEqual(["A1", "A2"]);
      expect(mockAction).not.toHaveBeenCalled();
    });

    it("add_item appends an empty string item locally", async () => {
      await renderStructural();
      fireEvent.click(screen.getByText("+ Tarefa"));
      await waitFor(() =>
        expect(screen.getAllByLabelText("Tarefa")).toHaveLength(2),
      );
      expect(mockAction).not.toHaveBeenCalled();
    });

    it("remove_item removes the string item locally", async () => {
      await renderStructural();
      fireEvent.click(screen.getByText("- Tarefa"));
      await waitFor(() =>
        expect(screen.queryByDisplayValue("t1")).toBeNull(),
      );
      expect(mockAction).not.toHaveBeenCalled();
    });

    it("remove_agent without an index param is a no-op", async () => {
      await renderStructural();
      fireEvent.click(screen.getByText("Remover sem indice"));
      const names = screen
        .getAllByLabelText("Nome")
        .map((el) => (el as HTMLInputElement).value);
      expect(names).toEqual(["A1", "A2"]);
      expect(mockAction).not.toHaveBeenCalled();
    });

    it("remove_item without an index param is a no-op", async () => {
      await renderStructural();
      fireEvent.click(screen.getByText("- Tarefa sem indice"));
      expect(screen.getByDisplayValue("t1")).toBeTruthy();
      expect(screen.getAllByLabelText("Tarefa")).toHaveLength(1);
      expect(mockAction).not.toHaveBeenCalled();
    });

    it("add_item on a path resolving to a non-array creates the array locally", async () => {
      // tools_integrations is ABSENT from the data model: resolveBind yields
      // undefined and mutateArray's `[]` fallback must create the array.
      const NONARRAY_TURN: AguiEvent[] = [
        {
          type: "CUSTOM",
          name: "a2ui",
          value: {
            messageType: "createSurface",
            surfaceId: "blueprint",
            root: "root",
          },
        },
        {
          type: "CUSTOM",
          name: "a2ui",
          value: {
            messageType: "updateComponents",
            surfaceId: "blueprint",
            components: [
              {
                id: "root",
                type: "Column",
                properties: {},
                children: ["frep", "addf"],
              },
              {
                id: "frep",
                type: "Repeater",
                properties: {
                  bind: "proposed_team/0/tools_integrations",
                  itemTemplate: "ftpl",
                },
                children: [],
              },
              {
                id: "ftpl",
                type: "TextInput",
                properties: { bind: ".", label: "Ferramenta" },
                children: [],
              },
              {
                id: "addf",
                type: "Button",
                properties: {
                  text: "+ Ferramenta",
                  action: {
                    name: "add_item",
                    params: { path: "proposed_team/0/tools_integrations" },
                  },
                },
                children: [],
              },
            ],
          },
        },
        {
          type: "CUSTOM",
          name: "a2ui",
          value: {
            messageType: "updateDataModel",
            surfaceId: "blueprint",
            data: { proposed_team: [{ name: "A1" }] },
          },
        },
        { type: "RUN_FINISHED", threadId: "t", runId: "r" },
      ];
      scriptTurn(NONARRAY_TURN);
      renderWithProviders(<DiscoveryPage />);
      fireEvent.click(screen.getByText("discovery.start"));
      await waitFor(() =>
        expect(screen.getByText("+ Ferramenta")).toBeTruthy(),
      );
      // Before the click the repeater has nothing to render (non-array).
      expect(screen.queryByLabelText("Ferramenta")).toBeNull();

      fireEvent.click(screen.getByText("+ Ferramenta"));

      await waitFor(() =>
        expect(screen.getAllByLabelText("Ferramenta")).toHaveLength(1),
      );
      // A second click appends to the now-existing array.
      fireEvent.click(screen.getByText("+ Ferramenta"));
      await waitFor(() =>
        expect(screen.getAllByLabelText("Ferramenta")).toHaveLength(2),
      );
      expect(mockAction).not.toHaveBeenCalled();
    });

    it("move_agent with a stale index === array length is a no-op", async () => {
      await renderStructural();
      // index 2 on a 2-agent team: j = 1 passes a naive `j < length` guard,
      // but swapping a[2] <-> a[1] would grow the array with an undefined
      // hole. It must leave the team untouched instead.
      fireEvent.click(screen.getByText("Subir 2 (stale)"));
      const names = screen
        .getAllByLabelText("Nome")
        .map((el) => (el as HTMLInputElement).value);
      expect(names).toEqual(["A1", "A2"]);
      expect(mockAction).not.toHaveBeenCalled();
    });
  });

  it("surfaces a RUN_ERROR as a visible error alert", async () => {
    scriptTurn([
      { type: "RUN_ERROR", message: "boom", code: "E1" },
      { type: "RUN_FINISHED", threadId: "t", runId: "r" },
    ]);
    renderWithProviders(<DiscoveryPage />);

    fireEvent.click(screen.getByText("discovery.start"));

    await waitFor(() => expect(screen.getByText(/boom/)).toBeTruthy());
  });
});
