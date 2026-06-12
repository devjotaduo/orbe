import { createElement, type ComponentType, type ReactNode } from "react";
import { Button, Card, Divider, Row, Tag, Typography } from "antd";
import styles from "./index.module.less";

/** Renderers receive resolved props + already-rendered children. */
export interface CatalogProps {
  properties: Record<string, unknown>;
  children?: ReactNode;
}

const text = (p: Record<string, unknown>): string => String(p.text ?? "");

/**
 * componentType → Ant Design renderer. Each entry maps one A2UI node type to a
 * theme-aware Ant Design component (works in light AND dark). Layout-only nodes
 * (Column/Row/List) lean on `.module.less` classes; the rest are antd
 * primitives that already respect the active theme tokens.
 */
export const A2UI_CATALOG: Record<string, ComponentType<CatalogProps>> = {
  Column: ({ children }) =>
    createElement("div", { className: styles.column }, children),
  Row: ({ children }) =>
    createElement(Row, { gutter: [8, 8] as [number, number] }, children),
  Card: ({ children }) => createElement(Card, { size: "small" }, children),
  List: ({ children }) =>
    createElement("div", { className: styles.list }, children),
  Heading: ({ properties }) =>
    createElement(
      Typography.Title,
      { level: 5, style: { margin: 0 } },
      text(properties),
    ),
  Text: ({ properties }) =>
    createElement(Typography.Text, null, text(properties)),
  Tag: ({ properties }) =>
    createElement(Tag, { color: "processing" }, text(properties)),
  Button: ({ properties }) =>
    createElement(Button, { size: "small" }, text(properties)),
  Divider: () => createElement(Divider, { style: { margin: "8px 0" } }),
};
