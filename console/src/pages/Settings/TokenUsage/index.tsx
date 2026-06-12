import { useCallback, useEffect, useMemo, useState } from "react";
import { DatePicker, Select } from "antd";
import { useTranslation } from "react-i18next";
import dayjs, { type Dayjs } from "dayjs";
import { useTheme } from "../../../contexts/ThemeContext";
import api from "../../../api";
import { authApi } from "../../../api/modules/auth";
import type { TokenUsageRecord } from "../../../api/types/tokenUsage";
import { useAppMessage } from "../../../hooks/useAppMessage";
import { PageHeader } from "@/components/PageHeader";
import {
  LoadingState,
  SummaryCards,
  ModelTrendChart,
  TokenTypeChart,
  DataTables,
  EmptyState,
} from "./components";
import { useDataAggregation } from "./hooks/useDataAggregation";
import { useModelTrendConfig } from "./hooks/useModelTrendConfig";
import { useTokenTypeConfig } from "./hooks/useTokenTypeConfig";
import styles from "./index.module.less";

function TokenUsagePage() {
  const { t } = useTranslation();
  const { message } = useAppMessage();
  const { isDark } = useTheme();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [records, setRecords] = useState<TokenUsageRecord[]>([]);
  const [startDate, setStartDate] = useState<Dayjs>(
    dayjs().subtract(30, "day"),
  );
  const [endDate, setEndDate] = useState<Dayjs>(dayjs());
  // Per-user filter — only offered when the current user has users.view
  // (multi-user installs with the enterprise extension). Without it the
  // page behaves exactly as before.
  const [canViewUsers, setCanViewUsers] = useState(false);
  const [users, setUsers] = useState<string[]>([]);
  const [selectedUser, setSelectedUser] = useState<string | undefined>(
    undefined,
  );

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(false);
    try {
      const detailsData = await api.getTokenUsageDetails({
        start_date: startDate.format("YYYY-MM-DD"),
        end_date: endDate.format("YYYY-MM-DD"),
        user: selectedUser,
      });
      setRecords(detailsData);
    } catch (err) {
      console.error("Failed to load token usage:", err);
      message.error(t("tokenUsage.loadFailed"));
      setRecords([]);
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate, selectedUser, message, t]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Resolve permissions once; degrade silently when auth is disabled or
  // the enterprise extension is missing (getMe throws).
  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const me = await authApi.getMe();
        if (!alive || !me.permissions.includes("users.view")) return;
        const list = await authApi.listUsers();
        if (!alive) return;
        setUsers(list.map((u) => u.username));
        setCanViewUsers(true);
      } catch {
        // No auth / no permission — keep the filter hidden.
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  const handleDateChange = (dates: [Dayjs | null, Dayjs | null] | null) => {
    if (!dates || !dates[0] || !dates[1]) return;
    setStartDate(dates[0]);
    setEndDate(dates[1]);
  };

  const aggregatedData = useDataAggregation(records);

  const modelTrendConfig = useModelTrendConfig({
    byDateModel: aggregatedData?.by_date_model ?? null,
    startDate,
    endDate,
    isDark,
  });

  const tokenTypeConfig = useTokenTypeConfig({
    byDate: aggregatedData?.by_date ?? null,
    startDate,
    endDate,
    isDark,
  });

  const byModelData = useMemo(() => {
    if (!aggregatedData?.by_model) return [];
    return Object.entries(aggregatedData.by_model).map(([key, stats]) => ({
      key,
      model: key,
      prompt_tokens: stats.prompt_tokens,
      completion_tokens: stats.completion_tokens,
      call_count: stats.call_count,
    }));
  }, [aggregatedData?.by_model]);

  const byDateData = useMemo(() => {
    if (!aggregatedData?.by_date) return [];
    return Object.entries(aggregatedData.by_date)
      .map(([date, stats]) => ({
        key: date,
        date,
        prompt_tokens: stats.prompt_tokens,
        completion_tokens: stats.completion_tokens,
        call_count: stats.call_count,
      }))
      .sort((a, b) => b.date.localeCompare(a.date));
  }, [aggregatedData?.by_date]);

  const pageHeader = (
    <PageHeader parent={t("nav.settings")} current={t("tokenUsage.title")} />
  );

  if (loading) {
    return (
      <div className={styles.container}>
        {pageHeader}
        <LoadingState message={t("common.loading", "Loading...")} />
      </div>
    );
  }

  if (error && records.length === 0) {
    return (
      <div className={styles.container}>
        {pageHeader}
        <LoadingState
          message={t("tokenUsage.loadFailed")}
          error
          onRetry={fetchData}
        />
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {pageHeader}

      <div className={styles.content}>
        <div className={styles.toolbar}>
          <DatePicker.RangePicker
            value={[startDate, endDate]}
            onChange={handleDateChange}
            disabledDate={(current) =>
              current && current.isAfter(dayjs(), "day")
            }
          />
          {canViewUsers && (
            <Select
              className={styles.userSelect}
              data-testid="token-usage-user-filter"
              allowClear
              showSearch
              placeholder={t("tokenUsage.allUsers")}
              aria-label={t("tokenUsage.filterByUser")}
              value={selectedUser}
              onChange={(value) => setSelectedUser(value)}
              options={users.map((u) => ({ value: u, label: u }))}
              optionFilterProp="label"
            />
          )}
        </div>

        {aggregatedData && (
          <SummaryCards
            totalCalls={aggregatedData.total_calls}
            totalPromptTokens={aggregatedData.total_prompt_tokens}
            totalCompletionTokens={aggregatedData.total_completion_tokens}
            totalTokens={
              aggregatedData.total_prompt_tokens +
              aggregatedData.total_completion_tokens
            }
          />
        )}

        <div className={styles.trendRow}>
          <ModelTrendChart chartConfig={modelTrendConfig} />
          <TokenTypeChart chartConfig={tokenTypeConfig} />
        </div>

        {byModelData.length === 0 && byDateData.length === 0 ? (
          <EmptyState message={t("tokenUsage.noData")} />
        ) : (
          <DataTables byModelData={byModelData} byDateData={byDateData} />
        )}
      </div>
    </div>
  );
}

export default TokenUsagePage;
