import type { WelcomeRenderProps } from "../../../../plugins/registry/types";
import { useAgentStore } from "../../../../stores/agentStore";
import styles from "./ChatWelcomeView.module.less";

// ── Avatar palette (chip fallback when image fails) ───────────────────────────
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

function seedColor(seed: string): [string, string] {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = seed.charCodeAt(i) + h * 31;
  return PALETTE[Math.abs(h) % PALETTE.length];
}

// DiceBear adventurer-neutral — illustrated soft avatars close to reference style
function dicebearUrl(seed: string, size = 80) {
  return `https://api.dicebear.com/8.x/adventurer-neutral/svg?seed=${encodeURIComponent(seed)}&size=${size}&backgroundColor=b6e3f4,c0aede,d1d4f9,ffd5dc,ffdfbf`;
}

interface AvatarImgProps {
  seed: string;
  size: number;
  className?: string;
  style?: React.CSSProperties;
}

function AvatarImg({ seed, size, className, style }: AvatarImgProps) {
  const [from, to] = seedColor(seed);
  return (
    <div
      className={className}
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        overflow: "hidden",
        background: `linear-gradient(135deg, ${from}, ${to})`,
        flexShrink: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: size * 0.36,
        fontWeight: 700,
        color: "#fff",
        userSelect: "none",
        ...style,
      }}
    >
      <img
        src={dicebearUrl(seed, size * 2)}
        alt={seed}
        width={size}
        height={size}
        style={{ width: size, height: size, display: "block" }}
        onError={(e) => {
          // fallback: hide img, show initials via background
          (e.currentTarget as HTMLImageElement).style.display = "none";
        }}
      />
    </div>
  );
}

// ── Mocked prompt cards ───────────────────────────────────────────────────────
const MOCK_CARDS = [
  { seed: "Patrick",  name: "Patrick · Slide Cr...",  sub: "Slides from bullet po...",     prompt: "Create a slide presentation from bullet points" },
  { seed: "Emily",    name: "Emily · Excel Crea...",   sub: "Pivot, chart & clean ...",     prompt: "Create an Excel spreadsheet with pivot tables and charts" },
  { seed: "Warren",   name: "Warren · Financi...",     sub: "DCF, cap tables, 3-stmt",      prompt: "Build a financial model with DCF and cap tables" },
  { seed: "Albert",   name: "Albert · Academi...",     sub: "Outline or full draft",         prompt: "Help me write an academic paper or full draft" },
  { seed: "Stella",   name: "Stella · UI/UX Desi...", sub: "Design with best pra...",       prompt: "Design a UI/UX following best practices" },
  { seed: "Marco",    name: "Marco · Morph PPT",       sub: "Cinematic presenta...",         prompt: "Create a cinematic PowerPoint presentation" },
  { seed: "William",  name: "William · Word Cr...",    sub: "Reports, proposals, l...",      prompt: "Write a professional report or proposal document" },
  { seed: "Carlos",   name: "Carlos · Cowork ...",     sub: "Complex tasks, end-...",        prompt: "Help me with a complex end-to-end workflow task" },
];

// ── Component ─────────────────────────────────────────────────────────────────

export function ChatWelcomeView({ greeting, onSubmit }: WelcomeRenderProps) {
  const { agents, selectedAgent, setSelectedAgent } = useAgentStore();

  const enabledAgents = (agents ?? []).filter((a) => a.enabled);
  const activeAgent   = enabledAgents.find((a) => a.id === selectedAgent);
  const otherAgents   = enabledAgents.filter((a) => a.id !== selectedAgent);
  const chipAgents    = activeAgent
    ? [activeAgent, ...otherAgents].slice(0, 9)
    : otherAgents.slice(0, 9);
  const moreChips     = Math.max(0, enabledAgents.length - 9);

  const label = (name: string, id: string) =>
    (name || id)
      .replace(/-/g, " ")
      .split(" ")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(" ");

  return (
    <div className={styles.root}>
      {/* ── Title ── */}
      <h1 className={styles.title}>{greeting || "Hi, what's your plan for today?"}</h1>

      {/* ── Agent chips ── */}
      {chipAgents.length > 0 && (
        <div className={styles.chips}>
          {chipAgents.map((a) => {
            const isActive = a.id === selectedAgent;
            return (
              <button
                key={a.id}
                className={`${styles.chip} ${isActive ? styles.chipActive : styles.chipIcon}`}
                onClick={() => setSelectedAgent(a.id)}
                title={label(a.name, a.id)}
              >
                <AvatarImg seed={a.id} size={22} />
                {isActive && (
                  <span className={styles.chipText}>{label(a.name, a.id)}</span>
                )}
              </button>
            );
          })}
          {moreChips > 0 && (
            <button className={`${styles.chip} ${styles.chipPlus}`}>+</button>
          )}
        </div>
      )}

      {/* ── "Select assistant" ── */}
      <p className={styles.selectLabel}>Select an assistant to start a task</p>

      {/* ── Mocked cards grid ── */}
      <div className={styles.grid}>
        {MOCK_CARDS.map((c, i) => (
          <button
            key={i}
            className={styles.card}
            onClick={() => onSubmit({ query: c.prompt })}
          >
            <AvatarImg seed={c.seed} size={46} className={styles.cardAvatar} />
            <div className={styles.cardBody}>
              <div className={styles.cardName}>{c.name}</div>
              <div className={styles.cardSub}>{c.sub}</div>
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
