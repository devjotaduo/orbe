/**
 * TokenUsage page — per-user filter (Fase 3 enterprise):
 *
 *  - the user Select appears ONLY when /auth/me grants `users.view`
 *    (loaded from GET /api/auth/users);
 *  - without the permission (or when getMe fails — auth disabled / no
 *    enterprise extension) the toolbar is identical to the original page;
 *  - the details request forwards the selected user as `user` param.
 *
 * Charts / tables / header are stubbed: this test targets the toolbar
 * permission gating and the API wiring, not the aggregation visuals.
 */
import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";

const testT = vi.hoisted(() =>
  vi.fn((key: string, fallback?: string) => fallback ?? key),
);
const testMessage = vi.hoisted(() => ({
  error: vi.fn(),
  success: vi.fn(),
}));

vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: testT,
  }),
}));

vi.mock("../../../contexts/ThemeContext", () => ({
  useTheme: () => ({ isDark: false }),
}));

vi.mock("../../../hooks/useAppMessage", () => ({
  useAppMessage: () => ({ message: testMessage }),
}));

vi.mock("@/components/PageHeader", () => ({
  PageHeader: () => <div data-testid="page-header" />,
}));

vi.mock("./components", () => ({
  LoadingState: ({ message }: { message: string }) => (
    <div data-testid="loading-state">{message}</div>
  ),
  SummaryCards: () => <div data-testid="summary-cards" />,
  ModelTrendChart: () => <div data-testid="model-trend" />,
  TokenTypeChart: () => <div data-testid="token-type" />,
  DataTables: () => <div data-testid="data-tables" />,
  EmptyState: ({ message }: { message: string }) => (
    <div data-testid="empty-state">{message}</div>
  ),
}));

vi.mock("./hooks/useDataAggregation", () => ({
  useDataAggregation: () => null,
}));
vi.mock("./hooks/useModelTrendConfig", () => ({
  useModelTrendConfig: () => ({}),
}));
vi.mock("./hooks/useTokenTypeConfig", () => ({
  useTokenTypeConfig: () => ({}),
}));

const getTokenUsageDetails = vi.fn();
vi.mock("../../../api", () => ({
  default: {
    getTokenUsageDetails: (...args: unknown[]) => getTokenUsageDetails(...args),
  },
}));

const getMe = vi.fn();
const listUsers = vi.fn();
vi.mock("../../../api/modules/auth", () => ({
  authApi: {
    getMe: (...args: unknown[]) => getMe(...args),
    listUsers: (...args: unknown[]) => listUsers(...args),
  },
}));

import TokenUsagePage from "./index";

describe("TokenUsage page — per-user filter", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getTokenUsageDetails.mockResolvedValue([]);
    listUsers.mockResolvedValue([
      { id: "1", username: "alice", roles: ["admin"], status: "active" },
      { id: "2", username: "bob", roles: ["viewer"], status: "active" },
    ]);
  });

  it("shows the user filter when the current user has users.view", async () => {
    getMe.mockResolvedValue({
      username: "admin",
      roles: ["admin"],
      permissions: ["users.view", "audit.view"],
    });

    render(<TokenUsagePage />);

    await waitFor(() =>
      expect(screen.getByTestId("token-usage-user-filter")).toBeInTheDocument(),
    );
    expect(listUsers).toHaveBeenCalledTimes(1);
  });

  it("hides the user filter without users.view", async () => {
    getMe.mockResolvedValue({
      username: "joe",
      roles: ["viewer"],
      permissions: ["chat.use"],
    });

    render(<TokenUsagePage />);

    // Wait for initial data load to settle, then assert absence.
    await waitFor(() => expect(getTokenUsageDetails).toHaveBeenCalled());
    await waitFor(() =>
      expect(screen.queryByTestId("loading-state")).not.toBeInTheDocument(),
    );
    expect(
      screen.queryByTestId("token-usage-user-filter"),
    ).not.toBeInTheDocument();
    expect(listUsers).not.toHaveBeenCalled();
  });

  it("hides the user filter when getMe fails (auth disabled / no extension)", async () => {
    getMe.mockRejectedValue(new Error("501"));

    render(<TokenUsagePage />);

    await waitFor(() => expect(getTokenUsageDetails).toHaveBeenCalled());
    await waitFor(() =>
      expect(screen.queryByTestId("loading-state")).not.toBeInTheDocument(),
    );
    expect(
      screen.queryByTestId("token-usage-user-filter"),
    ).not.toBeInTheDocument();
  });

  it("hides the user filter when listUsers fails after permission check", async () => {
    getMe.mockResolvedValue({
      username: "admin",
      roles: ["admin"],
      permissions: ["users.view"],
    });
    listUsers.mockRejectedValue(new Error("403"));

    render(<TokenUsagePage />);

    await waitFor(() => expect(getTokenUsageDetails).toHaveBeenCalled());
    await waitFor(() => expect(listUsers).toHaveBeenCalledTimes(1));
    expect(
      screen.queryByTestId("token-usage-user-filter"),
    ).not.toBeInTheDocument();
  });

  it("requests details without user param by default", async () => {
    getMe.mockResolvedValue({
      username: "admin",
      roles: ["admin"],
      permissions: ["users.view"],
    });

    render(<TokenUsagePage />);

    await waitFor(() => expect(getTokenUsageDetails).toHaveBeenCalled());
    const params = getTokenUsageDetails.mock.calls[0][0] as {
      start_date: string;
      end_date: string;
      user?: string;
    };
    expect(params.user).toBeUndefined();
    expect(params.start_date).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(params.end_date).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });
});
