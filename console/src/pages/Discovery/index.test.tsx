import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { screen, waitFor, fireEvent } from "@testing-library/react";
import { renderWithProviders } from "@/test/common_setup";
import type { AguiEvent } from "../../api/types/agui";
import DiscoveryPage from "./index";

const { mockStreamTurn } = vi.hoisted(() => ({ mockStreamTurn: vi.fn() }));

vi.mock("../../api/modules/discovery", () => ({
  discoveryApi: { streamTurn: mockStreamTurn },
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

describe("DiscoveryPage", () => {
  beforeEach(() => {
    mockStreamTurn.mockReset();
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
