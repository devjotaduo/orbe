import type { WelcomeRenderProps } from "../../../../plugins/registry/types";
import styles from "./ChatWelcomeView.module.less";

// Minimal SVG spark icon — no external dependency
function SparkIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 36 36"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <path
        d="M18 4 L20.5 15.5 L32 18 L20.5 20.5 L18 32 L15.5 20.5 L4 18 L15.5 15.5 Z"
        fill="currentColor"
        opacity="0.9"
      />
      <circle cx="27" cy="9" r="2.2" fill="currentColor" opacity="0.5" />
      <circle cx="9" cy="27" r="1.6" fill="currentColor" opacity="0.4" />
    </svg>
  );
}

export function ChatWelcomeView({
  greeting,
  description,
  prompts = [],
  onSubmit,
}: WelcomeRenderProps) {
  const handlePrompt = (value: string) => {
    onSubmit({ query: value });
  };

  return (
    <div className={styles.welcomeRoot}>
      <div className={styles.avatarWrap}>
        <SparkIcon className={styles.avatarIcon} />
      </div>

      {greeting && (
        <h1 className={styles.greeting}>{greeting}</h1>
      )}

      {description && (
        <p className={styles.description}>{description}</p>
      )}

      {prompts.length > 0 && (
        <div className={styles.promptList}>
          {prompts.map((p, i) => (
            <button
              key={i}
              className={styles.promptCard}
              onClick={() => handlePrompt(p.value)}
            >
              <span className={styles.promptLabel}>
                {p.label ?? p.value}
              </span>
              <span className={styles.promptArrow}>→</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
