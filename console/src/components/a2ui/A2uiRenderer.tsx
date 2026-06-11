import type { ReactNode } from "react";
import { Typography } from "antd";
import type { A2uiSurface } from "../../api/types/a2ui";
import { A2UI_CATALOG } from "./catalog";
import styles from "./index.module.less";

function renderNode(surface: A2uiSurface, id: string): ReactNode {
  const node = surface.components[id];
  if (!node) return null;

  const children = node.children.map((cid) => (
    <div key={cid} className={styles.node}>
      {renderNode(surface, cid)}
    </div>
  ));

  const Comp = A2UI_CATALOG[node.type];
  if (!Comp) {
    // Visible fallback — an unknown component type must never blank the screen.
    return (
      <Typography.Text type="warning">
        [{node.type}] {String(node.properties.text ?? "")}
      </Typography.Text>
    );
  }
  return <Comp properties={node.properties}>{children}</Comp>;
}

/** Walk the A2UI adjacency list from `surface.root` into Ant Design nodes. */
export function A2uiRenderer({ surface }: { surface: A2uiSurface }) {
  if (!surface.root) return null;
  return <>{renderNode(surface, surface.root)}</>;
}

export default A2uiRenderer;
