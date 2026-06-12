import type { WelcomeRenderProps } from "../../../../plugins/registry/types";
import { useAgentStore } from "../../../../stores/agentStore";
import styles from "./ChatWelcomeView.module.less";

// ── Avatar palette ────────────────────────────────────────────────────────────
const PALETTE: [string, string][] = [
  ["#7583b2", "#596590"],
  ["#ff7d00", "#c24b00"],
  ["#00b42a", "#007a1c"],
  ["#165dff", "#0040c4"],
  ["#f53f3f", "#b52020"],
  ["#722ed1", "#4a1a9e"],
  ["#0fc6c2", "#0a8c89"],
  ["#e68a00", "#9e5c00"],
];

function avatarColor(seed: string): [string, string] {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = seed.charCodeAt(i) + h * 31;
  return PALETTE[Math.abs(h) % PALETTE.length];
}

function initials(name: string): string {
  const words = name.replace(/-/g, " ").split(/\s+/).filter(Boolean);
  if (words.length === 1) return words[0].slice(0, 2).toUpperCase();
  return (words[0][0] + words[1][0]).toUpperCase();
}

function Avatar({ seed, size }: { seed: string; size: number }) {
  const [from, to] = avatarColor(seed);
  return (
    <div
      className={styles.avatar}
      style={{
        width: size,
        height: size,
        fontSize: size * 0.36,
        background: `linear-gradient(135deg, ${from}, ${to})`,
      }}
    >
      {initials(seed)}
    </div>
  );
}

// ── Mocked prompt cards (reference style) ────────────────────────────────────
const MOCK_CARDS = [
  { seed: "PA", name: "Patrick · Slide Cr...", sub: "Slides from bullet po...", prompt: "Create a slide presentation from bullet points" },
  { seed: "EM", name: "Emily · Excel Crea...", sub: "Pivot, chart & clean...", prompt: "Create an Excel spreadsheet with pivot tables and charts" },
  { seed: "WA", name: "Warren · Financi...", sub: "DCF, cap tables, 3-stmt", prompt: "Build a financial model with DCF and cap tables" },
  { seed: "AL", name: "Albert · Academi...", sub: "Outline or full draft", prompt: "Help me write an academic paper outline or full draft" },
  { seed: "ST", name: "Stella · UI/UX Desi...", sub: "Design with best pra...", prompt: "Design a UI/UX with best practices" },
  { seed: "MA", name: "Marco · Morph PPT", sub: "Cinematic presenta...", prompt: "Create a cinematic PowerPoint presentation" },
  { seed: "WI", name: "William · Word Cr...", sub: "Reports, proposals, l...", prompt: "Write a professional report or proposal" },
  { seed: "CA", name: "Carlos · Cowork ...", sub: "Complex tasks, end-...", prompt: "Help me with a complex end-to-end task" },
];

// ── Component ─────────────────────────────────────────────────────────────────

export function ChatWelcomeView({ greeting, onSubmit }: WelcomeRenderProps) {
  const { agents, selectedAgent, setSelectedAgent } = useAgentStore();

  const enabledAgents = (agents ?? []).filter((a) => a.enabled);
  const activeAgent = enabledAgents.find((a) => a.id === selectedAgent);
  const otherAgents = enabledAgents.filter((a) => a.id !== selectedAgent);
  const chipAgents = activeAgent
    ? [activeAgent, ...otherAgents].slice(0, 9)
    : otherAgents.slice(0, 9);
  const moreChips = Math.max(0, enabledAgents.length - 9);

  const agentLabel = (name: string, id: string) =>
    (name || id)
      .replace(/-/g, " ")
      .split(" ")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(" ");

  return (
    <div className={styles.welcomeRoot}>
      {/* Title */}
      <h1 className={styles.title}>{greeting || "Hi, what's your plan for today?"}</h1>

      {/* Agent chips row */}
      {chipAgents.length > 0 && (
        <div className={styles.chipsRow}>
          {chipAgents.map((a) => {
            const isActive = a.id === selectedAgent;
            return (
              <button
                key={a.id}
                className={`${styles.chip} ${isActive ? styles.chipActive : ""}`}
                onClick={() => setSelectedAgent(a.id)}
                title={agentLabel(a.name, a.id)}
              >
                <Avatar seed={a.id} size={22} />
                {isActive && (
                  <span className={styles.chipLabel}>
                    {agentLabel(a.name, a.id)}
                  </span>
                )}
              </button>
            );
          })}
          {moreChips > 0 && (
            <button className={`${styles.chip} ${styles.chipPlus}`}>+</button>
          )}
        </div>
      )}

      {/* "Select assistant" label */}
      <p className={styles.selectLabel}>Select an assistant to start a task</p>

      {/* Mocked prompt cards — 3-column grid */}
      <div className={styles.cardGrid}>
        {MOCK_CARDS.map((card, i) => (
          <button
            key={i}
            className={styles.card}
            onClick={() => onSubmit({ query: card.prompt })}
          >
            <Avatar seed={card.seed} size={44} />
            <div className={styles.cardInfo}>
              <div className={styles.cardName}>{card.name}</div>
              <div className={styles.cardSub}>{card.sub}</div>
            </div>
          </button>
        ))}
        <button className={`${styles.card} ${styles.cardMore}`}>
          +10 more
        </button>
      </div>
    </div>
  );
}
