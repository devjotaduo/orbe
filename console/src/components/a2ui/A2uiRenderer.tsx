import type { ReactNode } from "react";
import { Button, Input, Typography } from "antd";
import type { A2uiSurface } from "../../api/types/a2ui";
import { A2UI_CATALOG } from "./catalog";
import { joinBase, resolveBind, resolveProps, setPath } from "./binding";
import styles from "./index.module.less";

export interface A2uiRendererProps {
  surface: A2uiSurface;
  /** Data model to resolve binds against. Defaults to `surface.data`. */
  data?: Record<string, unknown>;
  /** Called with the next (immutable) data model when an editable field changes. */
  onDataChange?: (next: Record<string, unknown>) => void;
  /** Called when a Button carrying `properties.action` is activated. */
  onAction?: (name: string, params?: Record<string, unknown>) => void;
}

/** Render-time context threaded through the recursion. */
interface RenderCtx {
  data: Record<string, unknown>;
  basePath?: string;
  onDataChange?: A2uiRendererProps["onDataChange"];
  onAction?: A2uiRendererProps["onAction"];
}

function renderNode(
  surface: A2uiSurface,
  id: string,
  ctx: RenderCtx,
): ReactNode {
  const node = surface.components[id];
  if (!node) return null;
  const { data, basePath, onDataChange, onAction } = ctx;
  const resolved = resolveProps(node.properties, data, basePath);

  // Editable fields live here (not in the static catalog) because they need
  // the data model + onDataChange callback from the render context.
  if (node.type === "TextInput" || node.type === "TextArea") {
    const bindPath = joinBase(basePath, String(node.properties.bind ?? ""));
    const value = String(resolveBind(data, bindPath) ?? "");
    const label = resolved.label != null ? String(resolved.label) : "";
    const Field = node.type === "TextInput" ? Input : Input.TextArea;
    return (
      <label className={styles.field}>
        {label ? (
          <Typography.Text type="secondary" className={styles.fieldLabel}>
            {label}
          </Typography.Text>
        ) : null}
        <Field
          value={value}
          aria-label={label || bindPath}
          onChange={(e) =>
            onDataChange?.(setPath(data, bindPath, e.target.value))
          }
        />
      </label>
    );
  }

  // Buttons that carry an action dispatch through onAction; plain Buttons
  // (no action) still fall through to the static catalog below.
  if (node.type === "Button" && resolved.action) {
    const action = resolved.action as {
      name?: string;
      params?: Record<string, unknown>;
    };
    return (
      <Button
        type={resolved.variant === "primary" ? "primary" : "default"}
        onClick={() => onAction?.(String(action.name ?? ""), action.params)}
      >
        {String(resolved.text ?? "")}
      </Button>
    );
  }

  const children = node.children.map((cid) => (
    <div key={cid} className={styles.node}>
      {renderNode(surface, cid, ctx)}
    </div>
  ));

  const Comp = A2UI_CATALOG[node.type];
  if (!Comp) {
    // Visible fallback — an unknown component type must never blank the screen.
    return (
      <Typography.Text type="warning">
        [{node.type}] {String(resolved.text ?? "")}
      </Typography.Text>
    );
  }
  return <Comp properties={resolved}>{children}</Comp>;
}

/** Walk the A2UI adjacency list from `surface.root` into Ant Design nodes. */
export function A2uiRenderer({
  surface,
  data,
  onDataChange,
  onAction,
}: A2uiRendererProps) {
  if (!surface.root) return null;
  const ctx: RenderCtx = {
    data: data ?? surface.data,
    onDataChange,
    onAction,
  };
  return <>{renderNode(surface, surface.root, ctx)}</>;
}

export default A2uiRenderer;
