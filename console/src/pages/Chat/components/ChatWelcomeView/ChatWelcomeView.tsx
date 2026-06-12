import type { WelcomeRenderProps } from "../../../../plugins/registry/types";
import { useAgentStore } from "../../../../stores/agentStore";
import styles from "./ChatWelcomeView.module.less";

// ── Icon palette for agent chips ─────────────────────────────────────────────
const CHIP_COLORS = [
  "#1a1a2e",
  "#7c3aed",
  "#0891b2",
  "#065f46",
  "#9a3412",
  "#1e40af",
  "#6b21a8",
  "#0f766e",
];

function chipColor(id: string): string {
  let h = 0;
  for (let i = 0; i < id.length; i++) h = id.charCodeAt(i) + h * 31;
  return CHIP_COLORS[Math.abs(h) % CHIP_COLORS.length];
}

function initials(name: string, id: string): string {
  const s = name || id;
  const words = s.replace(/-/g, " ").split(/\s+/).filter(Boolean);
  if (words.length === 1) return words[0].slice(0, 2).toUpperCase();
  return (words[0][0] + words[1][0]).toUpperCase();
}

function agentLabel(name: string, id: string): string {
  return (name || id)
    .replace(/-/g, " ")
    .split(" ")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

// ── Mocked prompt cards — colorful app-icon style ─────────────────────────────
const MOCK_CARDS = [
  {
    icon: "⚡",
    color: "#ff6b35",
    bg: "#fff1ec",
    name: "Cowork",
    sub: "Autonomous task execution for complex workflows",
  },
  {
    icon: "🧜",
    color: "#e91e8c",
    bg: "#fff0f7",
    name: "Beautiful Mermaid",
    sub: "Create flowcharts, sequence diagrams and more",
  },
  {
    icon: "📊",
    color: "#1565c0",
    bg: "#e8f0fe",
    name: "PPT Creator",
    sub: "Create, edit, and analyze pro presentations",
  },
  {
    icon: "🎬",
    color: "#37474f",
    bg: "#f1f3f4",
    name: "3D Morph PPT",
    sub: "Turn a GLB 3D model into a cinematic slide",
  },
  {
    icon: "🎯",
    color: "#c62828",
    bg: "#fce4e4",
    name: "Pitch Deck Creator",
    sub: "Build investor pitch decks, pr...",
  },
  {
    icon: "🎮",
    color: "#1b5e20",
    bg: "#e8f5e9",
    name: "3D Game",
    sub: "Generate a complete 3D platform game",
  },
  {
    icon: "📖",
    color: "#78909c",
    bg: "#f5f5f5",
    name: "Story Roleplay",
    sub: "Immersive story roleplay experience",
  },
  {
    icon: "📋",
    color: "#546e7a",
    bg: "#eceff1",
    name: "Star Office Helper",
    sub: "Install, connect, and troubleshoot office apps",
  },
  {
    icon: "📈",
    color: "#00838f",
    bg: "#e0f7fa",
    name: "Dashboard Creator",
    sub: "Turn CSV or tabular data into dashboards",
  },
];

// ── Component ─────────────────────────────────────────────────────────────────

export function ChatWelcomeView({ greeting, onSubmit }: WelcomeRenderProps) {
  const { agents, selectedAgent, setSelectedAgent } = useAgentStore();

  const enabled = (agents ?? []).filter((a) => a.enabled);
  const active = enabled.find((a) => a.id === selectedAgent);
  const others = enabled.filter((a) => a.id !== selectedAgent);
  const chipOthers = others.slice(0, 10);
  const moreCount = Math.max(0, enabled.length - 1 - chipOthers.length);

  return (
    <div className={styles.root}>
      {/* ── Title ── */}
      <h1 className={styles.title}>
        {greeting || "Hi, what's your plan for today?"}
      </h1>

      {/* ── Single pill agent row ── */}
      {enabled.length > 0 && (
        <div className={styles.agentPill}>
          {/* Active agent — shows label */}
          {active && (
            <>
              <button
                className={styles.agentActive}
                onClick={() => setSelectedAgent(active.id)}
              >
                <span
                  className={styles.agentIcon}
                  style={{ background: chipColor(active.id) }}
                >
                  {initials(active.name, active.id)}
                </span>
                <span className={styles.agentName}>
                  {agentLabel(active.name, active.id)}
                </span>
              </button>
              {chipOthers.length > 0 && <span className={styles.sep}>|</span>}
            </>
          )}

          {/* Other agents — icon only with separators */}
          {chipOthers.map((a, i) => (
            <span key={a.id} className={styles.agentIconRow}>
              <button
                className={styles.agentIconBtn}
                onClick={() => setSelectedAgent(a.id)}
                title={agentLabel(a.name, a.id)}
              >
                <span
                  className={styles.agentIcon}
                  style={{ background: chipColor(a.id) }}
                >
                  {initials(a.name, a.id)}
                </span>
              </button>
              {i < chipOthers.length - 1 && (
                <span className={styles.sep}>|</span>
              )}
            </span>
          ))}

          {/* More + */}
          {(moreCount > 0 || enabled.length > 0) && (
            <>
              <span className={styles.sep}>|</span>
              <button className={styles.agentPlusBtn}>+</button>
            </>
          )}
        </div>
      )}

      {/* ── "Select an assistant" ── */}
      <p className={styles.selectLabel}>Select an assistant to start a task</p>

      {/* ── Cards grid ── */}
      <div className={styles.grid}>
        {MOCK_CARDS.map((c, i) => (
          <button
            key={i}
            className={styles.card}
            onClick={() => onSubmit({ query: c.name })}
          >
            <span
              className={styles.cardIcon}
              style={{ background: c.bg, color: c.color }}
            >
              {c.icon}
            </span>
            <div className={styles.cardBody}>
              <div className={styles.cardName}>{c.name}</div>
              <div className={styles.cardSub}>{c.sub}</div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
