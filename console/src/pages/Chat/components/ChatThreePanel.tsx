import {
  useRef,
  useState,
  useCallback,
  useEffect,
  type ReactNode,
} from "react";
import { FileTextOutlined, AppstoreOutlined, CloseOutlined } from "@ant-design/icons";
import styles from "./ChatThreePanel.module.less";

interface ChatThreePanelProps {
  chat: ReactNode;
  preview?: ReactNode;
  workspace?: ReactNode;
}

const STORAGE_KEY_PREVIEW_W = "qwenpaw-panel-preview-w";
const STORAGE_KEY_WORKSPACE_W = "qwenpaw-panel-workspace-w";

function loadWidth(key: string, fallback: number): number {
  try {
    return parseInt(localStorage.getItem(key) || String(fallback), 10) || fallback;
  } catch {
    return fallback;
  }
}

export function ChatThreePanel({ chat, preview, workspace }: ChatThreePanelProps) {
  const [previewOpen, setPreviewOpen] = useState(false);
  const [workspaceOpen, setWorkspaceOpen] = useState(false);
  const [previewW, setPreviewW] = useState(() => loadWidth(STORAGE_KEY_PREVIEW_W, 380));
  const [workspaceW, setWorkspaceW] = useState(() => loadWidth(STORAGE_KEY_WORKSPACE_W, 320));

  // Drag state
  const draggingPanel = useRef<"preview" | "workspace" | null>(null);
  const dragStartX = useRef(0);
  const dragStartW = useRef(0);
  const previewWRef = useRef(previewW);
  const workspaceWRef = useRef(workspaceW);

  useEffect(() => { previewWRef.current = previewW; }, [previewW]);
  useEffect(() => { workspaceWRef.current = workspaceW; }, [workspaceW]);

  const handleDragStart = useCallback(
    (panel: "preview" | "workspace") =>
      (e: React.MouseEvent) => {
        e.preventDefault();
        draggingPanel.current = panel;
        dragStartX.current = e.clientX;
        dragStartW.current =
          panel === "preview" ? previewWRef.current : workspaceWRef.current;
        document.body.style.userSelect = "none";
        document.body.style.cursor = "col-resize";

        const onMove = (me: MouseEvent) => {
          if (!draggingPanel.current) return;
          // dragging left edge → increasing width means moving handle left
          const delta = dragStartX.current - me.clientX;
          const next = Math.min(Math.max(dragStartW.current + delta, 220), 620);
          if (panel === "preview") setPreviewW(next);
          else setWorkspaceW(next);
        };

        const onUp = () => {
          draggingPanel.current = null;
          document.body.style.userSelect = "";
          document.body.style.cursor = "";
          try {
            if (panel === "preview")
              localStorage.setItem(STORAGE_KEY_PREVIEW_W, String(previewWRef.current));
            else
              localStorage.setItem(STORAGE_KEY_WORKSPACE_W, String(workspaceWRef.current));
          } catch {}
          document.removeEventListener("mousemove", onMove);
          document.removeEventListener("mouseup", onUp);
        };

        document.addEventListener("mousemove", onMove);
        document.addEventListener("mouseup", onUp);
      },
    [],
  );

  const hasPreview = !!preview;
  const hasWorkspace = !!workspace;

  return (
    <div className={styles.threePanelRoot}>
      {/* Main chat panel */}
      <div className={`${styles.panel} ${styles.panelMain}`}>
        {chat}

        {/* Toggle strip — only show when at least one extra panel is available */}
        {(hasPreview || hasWorkspace) && (
          <div className={styles.panelToggleBar}>
            {hasPreview && (
              <button
                className={`${styles.toggleBtn} ${previewOpen ? styles.toggleBtnActive : ""}`}
                onClick={() => setPreviewOpen((v) => !v)}
                title="Preview"
              >
                <FileTextOutlined style={{ fontSize: 12 }} />
              </button>
            )}
            {hasWorkspace && (
              <button
                className={`${styles.toggleBtn} ${workspaceOpen ? styles.toggleBtnActive : ""}`}
                onClick={() => setWorkspaceOpen((v) => !v)}
                title="Workspace"
              >
                <AppstoreOutlined style={{ fontSize: 12 }} />
              </button>
            )}
          </div>
        )}
      </div>

      {/* Preview panel */}
      {hasPreview && previewOpen && (
        <div
          className={`${styles.panel} ${styles.panelPreview}`}
          style={{ width: previewW }}
        >
          {/* drag handle on the left edge */}
          <div
            className={styles.dragHandle}
            onMouseDown={handleDragStart("preview")}
          />
          <div className={styles.panelHeader}>
            <FileTextOutlined style={{ fontSize: 13, opacity: 0.6 }} />
            <span className={styles.panelTitle}>Preview</span>
            <button
              className={styles.panelCloseBtn}
              onClick={() => setPreviewOpen(false)}
            >
              <CloseOutlined />
            </button>
          </div>
          <div className={styles.panelContent}>{preview}</div>
        </div>
      )}

      {/* Workspace panel */}
      {hasWorkspace && workspaceOpen && (
        <div
          className={`${styles.panel} ${styles.panelWorkspace}`}
          style={{ width: workspaceW }}
        >
          <div
            className={styles.dragHandle}
            onMouseDown={handleDragStart("workspace")}
          />
          <div className={styles.panelHeader}>
            <AppstoreOutlined style={{ fontSize: 13, opacity: 0.6 }} />
            <span className={styles.panelTitle}>Workspace</span>
            <button
              className={styles.panelCloseBtn}
              onClick={() => setWorkspaceOpen(false)}
            >
              <CloseOutlined />
            </button>
          </div>
          <div className={styles.panelContent}>{workspace}</div>
        </div>
      )}
    </div>
  );
}
