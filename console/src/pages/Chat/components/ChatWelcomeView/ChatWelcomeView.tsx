import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import type { WelcomeRenderProps } from "../../../../plugins/registry/types";
import { useAgentStore } from "../../../../stores/agentStore";
import styles from "./ChatWelcomeView.module.less";

// ── Avatar color palette ──────────────────────────────────────────────────────
const PALETTE: [string, string][] = [
  ["#7583b2", "#596590"],
  ["#ff7d00", "#c24b00"],
  ["#00b42a", "#007a1c"],
  ["#165dff", "#0040c4"],
  ["#f53f3f", "#b52020"],
  ["#722ed1", "#4a1a9e"],
  ["#0fc6c2", "#0a8c89"],
  ["#f77234", "#c44a10"],
];

function avatarColors(seed: string): [string, string] {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = seed.charCodeAt(i) + h * 31;
  return PALETTE[Math.abs(h) % PALETTE.length];
}

function initials(name: string): string {
  const words = name.replace(/-/g, " ").split(/\s+/).filter(Boolean);
  if (words.length === 1) return words[0].slice(0, 2).toUpperCase();
  return (words[0][0] + words[1][0]).toUpperCase();
}

function AgentAvatar({
  id,
  name,
  size,
  className,
}: {
  id: string;
  name: string;
  size: number;
  className?: string;
}) {
  const [from, to] = avatarColors(id);
  return (
    <div
      className={className}
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        background: `linear-gradient(135deg, ${from}, ${to})`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: size * 0.36,
        fontWeight: 700,
        color: "#fff",
        flexShrink: 0,
        userSelect: "none",
      }}
    >
      {initials(name || id)}
    </div>
  );
}

// ── Component ─────────────────────────────────────────────────────────────────

export function ChatWelcomeView({
  greeting,
  prompts = [],
  onSubmit,
}: WelcomeRenderProps) {
  const navigate = useNavigate();
  const { agents, selectedAgent, setSelectedAgent } = useAgentStore();
  const [inputValue, setInputValue] = useState("");

  const enabledAgents = (agents ?? []).filter((a) => a.enabled);
  // Icon row: active agent first, then others (max 8 total)
  const activeAgent = enabledAgents.find((a) => a.id === selectedAgent);
  const otherAgents = enabledAgents.filter((a) => a.id !== selectedAgent);
  const chipAgents = activeAgent
    ? [activeAgent, ...otherAgents].slice(0, 8)
    : otherAgents.slice(0, 8);
  const moreChips = Math.max(0, enabledAgents.length - 8);

  // Cards: show up to 8 agents in 3-col grid
  const cardAgents = enabledAgents.slice(0, 8);
  const moreCards = Math.max(0, enabledAgents.length - 8);

  const handleSend = useCallback(() => {
    const text = inputValue.trim();
    if (!text) return;
    setInputValue("");
    onSubmit({ query: text });
  }, [inputValue, onSubmit]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSelectAgent = (id: string) => {
    setSelectedAgent(id);
    navigate("/chat");
  };

  const displayTitle =
    greeting || "Hi, what's your plan for today?";

  const agentLabel = (name: string | undefined, id: string) =>
    (name || id)
      .replace(/-/g, " ")
      .split(" ")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(" ");

  return (
    <div className={styles.welcomeRoot}>
      {/* ── Title ── */}
      <h1 className={styles.title}>{displayTitle}</h1>

      {/* ── Agent icon chips ── */}
      {chipAgents.length > 0 && (
        <div className={styles.agentChipsRow}>
          {chipAgents.map((a) => {
            const isActive = a.id === selectedAgent;
            return (
              <button
                key={a.id}
                className={`${styles.agentChip} ${isActive ? styles.agentChipActive : ""} ${!isActive ? styles.agentChipIconOnly : ""}`}
                onClick={() => setSelectedAgent(a.id)}
                title={agentLabel(a.name, a.id)}
              >
                <AgentAvatar
                  id={a.id}
                  name={a.name || a.id}
                  size={24}
                  className={styles.agentChipAvatar}
                />
                {isActive && (
                  <span>{agentLabel(a.name, a.id)}</span>
                )}
              </button>
            );
          })}
          {moreChips > 0 && (
            <button className={`${styles.agentChip} ${styles.agentChipMore}`}>
              +
            </button>
          )}
        </div>
      )}

      {/* ── Input box ── */}
      <div className={styles.inputBox}>
        <textarea
          className={styles.inputTextarea}
          placeholder="Send a message, upload files, or describe a task..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={2}
          autoFocus
        />
        <div className={styles.inputBar}>
          <div className={styles.inputTags}>
            {activeAgent && (
              <span className={styles.inputTag}>
                {agentLabel(activeAgent.name, activeAgent.id)}
              </span>
            )}
          </div>
          <button
            className={`${styles.sendBtn} ${inputValue.trim() ? styles.sendBtnActive : ""}`}
            onClick={handleSend}
            disabled={!inputValue.trim()}
            aria-label="Send"
          >
            ↑
          </button>
        </div>
      </div>

      {/* ── Agent cards ── */}
      {cardAgents.length > 0 && (
        <>
          <p className={styles.selectLabel}>Select an assistant to start a task</p>
          <div className={styles.agentGrid}>
            {cardAgents.map((a) => (
              <button
                key={a.id}
                className={styles.agentCard}
                onClick={() => handleSelectAgent(a.id)}
              >
                <AgentAvatar
                  id={a.id}
                  name={a.name || a.id}
                  size={44}
                  className={styles.agentAvatar}
                />
                <div className={styles.agentCardInfo}>
                  <div className={styles.agentCardName}>
                    {agentLabel(a.name, a.id)}
                  </div>
                  {a.description && (
                    <div className={styles.agentCardDesc}>{a.description}</div>
                  )}
                </div>
              </button>
            ))}
            {moreCards > 0 && (
              <button className={`${styles.agentCard} ${styles.agentCardMore}`}>
                +{moreCards} more
              </button>
            )}
          </div>
        </>
      )}

      {/* ── Prompt fallback when no agents ── */}
      {cardAgents.length === 0 && prompts.length > 0 && (
        <div className={styles.promptList}>
          {prompts.map((p, i) => (
            <button
              key={i}
              className={styles.promptCard}
              onClick={() => onSubmit({ query: p.value })}
            >
              <span>{p.label ?? p.value}</span>
              <span className={styles.promptArrow}>→</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
