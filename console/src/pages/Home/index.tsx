import { useTranslation } from "react-i18next";
import { Button } from "antd";
import {
  BugOutlined,
  StarOutlined,
  GlobalOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import styles from "./index.module.less";

// Static assistant card data — icons are emoji strings to avoid asset deps.
const ASSISTANT_CARDS = [
  {
    key: "chat",
    emoji: "💬",
    nameKey: "home.assistants.chat.name",
    descKey: "home.assistants.chat.desc",
    path: "/chat",
  },
  {
    key: "coding",
    emoji: "💻",
    nameKey: "home.assistants.coding.name",
    descKey: "home.assistants.coding.desc",
    path: "/coding",
  },
  {
    key: "agent",
    emoji: "🤖",
    nameKey: "home.assistants.agent.name",
    descKey: "home.assistants.agent.desc",
    path: "/sessions",
  },
  {
    key: "inbox",
    emoji: "📬",
    nameKey: "home.assistants.inbox.name",
    descKey: "home.assistants.inbox.desc",
    path: "/inbox",
  },
  {
    key: "workspace",
    emoji: "🗂️",
    nameKey: "home.assistants.workspace.name",
    descKey: "home.assistants.workspace.desc",
    path: "/workspace",
  },
  {
    key: "mcp",
    emoji: "🔌",
    nameKey: "home.assistants.mcp.name",
    descKey: "home.assistants.mcp.desc",
    path: "/mcp",
  },
] as const;

// Backend selector pills
const PILL_LABELS = [
  { key: "all", labelKey: "home.pills.all" },
  { key: "chat", labelKey: "home.pills.chat" },
  { key: "code", labelKey: "home.pills.code" },
  { key: "agent", labelKey: "home.pills.agent" },
] as const;

export default function HomePage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const activePill = "all";

  return (
    <div className={styles.root}>
      <div className={styles.centerCol}>
        {/* Greeting */}
        <h1 className={styles.greeting}>{t("home.greeting")}</h1>

        {/* PillBar */}
        <div className={styles.pillBar} role="tablist" aria-label={t("home.pillBar.label")}>
          {PILL_LABELS.map(({ key, labelKey }) => (
            <button
              key={key}
              role="tab"
              aria-selected={key === activePill}
              className={
                key === activePill
                  ? `${styles.pill} ${styles.pillActive}`
                  : styles.pill
              }
            >
              {t(labelKey)}
            </button>
          ))}
        </div>

        {/* Assistant cards grid */}
        <div className={styles.cardGrid} role="list">
          {ASSISTANT_CARDS.map((card) => (
            <button
              key={card.key}
              role="listitem"
              className={styles.card}
              onClick={() => navigate(card.path)}
              aria-label={t(card.nameKey)}
            >
              <span className={styles.cardEmoji} aria-hidden="true">
                {card.emoji}
              </span>
              <span className={styles.cardName}>{t(card.nameKey)}</span>
              <span className={styles.cardDesc}>{t(card.descKey)}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Floating footer */}
      <div className={styles.footer} role="toolbar" aria-label={t("home.footer.label")}>
        <Button
          type="text"
          shape="circle"
          icon={<BugOutlined />}
          className={styles.footerBtn}
          title={t("home.footer.reportIssue")}
          aria-label={t("home.footer.reportIssue")}
        />
        <Button
          type="text"
          shape="circle"
          icon={<StarOutlined />}
          className={styles.footerBtn}
          title={t("home.footer.star")}
          aria-label={t("home.footer.star")}
        />
        <Button
          type="text"
          shape="circle"
          icon={<GlobalOutlined />}
          className={styles.footerBtn}
          title={t("home.footer.remote")}
          aria-label={t("home.footer.remote")}
        />
      </div>
    </div>
  );
}
