import { useCallback, useEffect, useRef, useState } from "react";
import {
  Alert,
  Button,
  Card,
  Empty,
  Input,
  Space,
  Spin,
  Typography,
  theme,
} from "antd";
import {
  SendOutlined,
  CompassOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { PageHeader } from "@/components/PageHeader";
import { discoveryApi } from "../../api/modules/discovery";
import type { AguiEvent } from "../../api/types/agui";
import type { A2uiMessage, A2uiSurface } from "../../api/types/a2ui";
import {
  applyA2uiMessage,
  emptySurface,
} from "../../components/a2ui/surfaceReducer";
import { A2uiRenderer } from "../../components/a2ui/A2uiRenderer";
import styles from "./index.module.less";

type Turn = { role: "agent" | "user"; text: string };

export default function DiscoveryPage() {
  const { t } = useTranslation();
  const { token } = theme.useToken();

  const sessionId = useRef(`sess-${Date.now()}`).current;
  const [transcript, setTranscript] = useState<Turn[]>([]);
  const [state, setState] = useState<Record<string, unknown>>({});
  const [surface, setSurface] = useState<A2uiSurface | null>(null);
  const surfaceRef = useRef<A2uiSurface | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [started, setStarted] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Client-side editable copy of the surface data model (binds write here).
  const [dataModel, setDataModel] = useState<Record<string, unknown> | null>(
    null,
  );
  const [approved, setApproved] = useState(false);
  const [approving, setApproving] = useState(false);
  const [approveError, setApproveError] = useState<string | null>(null);

  const transcriptEndRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [transcript, surface]);

  // Abort an in-flight turn if the page unmounts mid-stream.
  useEffect(() => {
    return () => {
      abortRef.current?.abort();
    };
  }, []);

  const runTurn = useCallback(
    async (message: string | null) => {
      // Cancel any still-running turn before starting a new one.
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;
      setBusy(true);
      setError(null);
      let pendingText = "";
      let gotSurface = false;
      try {
        await discoveryApi.streamTurn(
          sessionId,
          message,
          (ev: AguiEvent) => {
          switch (ev.type) {
            case "TEXT_MESSAGE_CONTENT":
              pendingText += ev.delta;
              break;
            case "STATE_SNAPSHOT":
              setState(ev.snapshot);
              break;
            case "CUSTOM":
              if (ev.name === "a2ui") {
                gotSurface = true;
                const next = applyA2uiMessage(
                  surfaceRef.current ?? emptySurface("blueprint"),
                  ev.value as unknown as A2uiMessage,
                );
                surfaceRef.current = next;
                setSurface({ ...next });
              }
              break;
            case "RUN_ERROR":
              setError(ev.message);
              break;
            default:
              break;
          }
          },
          controller.signal,
        );
        // The interview is complete only when a turn delivered the blueprint
        // surface (the backend emits A2UI + closes the session on the final
        // turn). Gating on this — not on `surface !== null` at render time —
        // keeps the composer alive if a future mid-interview CUSTOM a2ui event
        // ever arrives without ending the run.
        if (gotSurface) {
          setDone(true);
          // Seed the editable data model from the surface exactly once, so
          // later surface updates never clobber in-progress user edits.
          setDataModel(
            (prev) => prev ?? { ...(surfaceRef.current?.data ?? {}) },
          );
        }
      } catch (err) {
        // Aborts (unmount / restart / superseded turn) are intentional.
        if (controller.signal.aborted) return;
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        if (!controller.signal.aborted && pendingText) {
          setTranscript((prev) => [...prev, { role: "agent", text: pendingText }]);
        }
        // Only the latest turn clears the busy flag / its controller.
        if (abortRef.current === controller) {
          setBusy(false);
          abortRef.current = null;
        }
      }
    },
    [sessionId],
  );

  const start = useCallback(async () => {
    setStarted(true);
    await runTurn(null);
  }, [runTurn]);

  const send = useCallback(async () => {
    const msg = input.trim();
    if (!msg || busy) return;
    setTranscript((prev) => [...prev, { role: "user", text: msg }]);
    setInput("");
    await runTurn(msg);
  }, [input, busy, runTurn]);

  // approve_team: POST the client-edited data model; the backend validates it
  // against TeamBlueprint and persists blueprint.json/.md. RUN_ERROR keeps the
  // edits intact so the user can fix the field and retry.
  const approve = useCallback(async () => {
    if (!dataModel || approving || approved) return;
    // Own an AbortController (same pattern as runTurn) so restart()/unmount
    // cancels an in-flight approve and a late resolution can never mark a
    // freshly restarted session as approved.
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setApproving(true);
    setApproveError(null);
    let failed = false;
    try {
      await discoveryApi.action(
        sessionId,
        "approve_team",
        dataModel,
        (ev: AguiEvent) => {
          if (ev.type === "RUN_ERROR") {
            failed = true;
            setApproveError(ev.message);
          }
        },
        controller.signal,
      );
      if (!controller.signal.aborted && !failed) setApproved(true);
    } catch (err) {
      // Aborts (restart / unmount / superseded request) are intentional.
      if (controller.signal.aborted) return;
      setApproveError(err instanceof Error ? err.message : String(err));
    } finally {
      // Only the latest request clears the busy flag / its controller.
      if (abortRef.current === controller) {
        setApproving(false);
        abortRef.current = null;
      }
    }
  }, [dataModel, approving, approved, sessionId]);

  const handleAction = useCallback(
    (name: string) => {
      if (name === "approve_team") void approve();
      // Structural actions (add/remove/move) arrive in Fase 2.
    },
    [approve],
  );

  const restart = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    surfaceRef.current = null;
    setTranscript([]);
    setState({});
    setSurface(null);
    setInput("");
    setError(null);
    setDone(false);
    setBusy(false);
    setStarted(false);
    setDataModel(null);
    setApproved(false);
    setApproving(false);
    setApproveError(null);
  }, []);

  const completed = done;

  return (
    <div className={styles.page}>
      <PageHeader current={t("discovery.title")} />
      <div className={styles.content}>
        <div className={styles.inner}>
          {!started ? (
            <div className={styles.intro}>
              <div className={styles.introIcon} style={{ color: token.colorPrimary }}>
                <CompassOutlined />
              </div>
              <Typography.Title level={3} style={{ marginTop: 0 }}>
                {t("discovery.subtitle")}
              </Typography.Title>
              <Typography.Paragraph
                type="secondary"
                className={styles.introText}
              >
                {t("discovery.intro")}
              </Typography.Paragraph>
              <Button
                type="primary"
                size="large"
                icon={<CompassOutlined />}
                onClick={start}
                loading={busy}
              >
                {t("discovery.start")}
              </Button>
            </div>
          ) : (
            <>
              {error && (
                <Alert
                  type="error"
                  showIcon
                  message={`${t("discovery.errorPrefix")}: ${error}`}
                  action={
                    <Button
                      size="small"
                      icon={<ReloadOutlined />}
                      onClick={restart}
                    >
                      {t("discovery.restart")}
                    </Button>
                  }
                />
              )}

              <div className={styles.transcript} aria-live="polite">
                {transcript.map((turn, i) => (
                  <div
                    key={i}
                    className={`${styles.turn} ${
                      turn.role === "user" ? styles.turnUser : styles.turnAgent
                    }`}
                  >
                    <div
                      className={styles.bubble}
                      style={{
                        background:
                          turn.role === "user"
                            ? token.colorPrimary
                            : token.colorFillSecondary,
                        color:
                          turn.role === "user"
                            ? token.colorTextLightSolid
                            : token.colorText,
                      }}
                    >
                      <span className={styles.role}>
                        {turn.role === "user"
                          ? t("discovery.you")
                          : t("discovery.agent")}
                      </span>
                      {turn.text}
                    </div>
                  </div>
                ))}
                {busy && transcript.length === 0 && (
                  <div className={styles.turn + " " + styles.turnAgent}>
                    <Spin size="small" />
                  </div>
                )}
              </div>

              {!completed && (
                <Space.Compact className={styles.composer}>
                  <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onPressEnter={send}
                    placeholder={t("discovery.answerPlaceholder")}
                    disabled={busy}
                    aria-label={t("discovery.answerPlaceholder")}
                  />
                  <Button
                    type="primary"
                    icon={<SendOutlined />}
                    onClick={send}
                    loading={busy}
                  >
                    {t("discovery.send")}
                  </Button>
                </Space.Compact>
              )}

              {completed && (
                <Card
                  className={styles.surfaceCard}
                  title={t("discovery.teamTitle")}
                  extra={
                    <Button
                      size="small"
                      icon={<ReloadOutlined />}
                      onClick={restart}
                    >
                      {t("discovery.restart")}
                    </Button>
                  }
                >
                  {approved ? (
                    <Alert
                      type="success"
                      showIcon
                      message={t("discovery.approvedTitle")}
                      description={t("discovery.approved")}
                    />
                  ) : surface && surface.root ? (
                    <>
                      {approveError && (
                        <Alert
                          type="error"
                          showIcon
                          className={styles.approveAlert}
                          message={t("discovery.approveError")}
                          description={approveError}
                        />
                      )}
                      <Spin spinning={approving}>
                        <A2uiRenderer
                          surface={surface}
                          data={dataModel ?? undefined}
                          onDataChange={setDataModel}
                          onAction={handleAction}
                        />
                      </Spin>
                    </>
                  ) : (
                    <Empty
                      image={Empty.PRESENTED_IMAGE_SIMPLE}
                      description={t("discovery.completed")}
                    />
                  )}
                </Card>
              )}

              <details className={styles.debug}>
                <summary>{t("discovery.statePanel")}</summary>
                <pre
                  className={styles.debugPre}
                  style={{
                    background: token.colorFillTertiary,
                    color: token.colorTextSecondary,
                  }}
                >
                  {JSON.stringify(state, null, 2)}
                </pre>
              </details>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
