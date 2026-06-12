import { useRef, useEffect, useLayoutEffect, type CSSProperties } from "react";
import { createRoot, type Root } from "react-dom/client";
import { XMarkdown } from "@ant-design/x-markdown";
import type { XMarkdownProps } from "@ant-design/x-markdown";

interface ShadowMarkdownProps {
  content: string;
  components?: XMarkdownProps["components"];
  dompurifyConfig?: XMarkdownProps["dompurifyConfig"];
  style?: CSSProperties;
  className?: string;
}

// CSS custom properties that should be forwarded from :root into :host
function buildHostVars(): string {
  const style = getComputedStyle(document.documentElement);
  const props: string[] = [];
  for (let i = 0; i < style.length; i++) {
    const name = style[i];
    if (name.startsWith("--")) {
      props.push(`${name}: ${style.getPropertyValue(name)};`);
    }
  }
  return `:host { ${props.join(" ")} }`;
}

// Minimal prose reset so markdown looks good without antd leaking in
const PROSE_CSS = `
  :host {
    display: block;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 14px;
    line-height: 1.7;
    color: inherit;
  }
  * { box-sizing: border-box; }
  h1, h2, h3, h4, h5, h6 {
    margin: 1em 0 0.4em;
    font-weight: 600;
    line-height: 1.3;
  }
  h1 { font-size: 1.6em; } h2 { font-size: 1.3em; } h3 { font-size: 1.1em; }
  p { margin: 0.6em 0; }
  a { color: #165dff; text-decoration: none; }
  a:hover { text-decoration: underline; }
  blockquote {
    margin: 0.8em 0;
    padding: 0 1em;
    border-left: 3px solid #d1d5e5;
    color: #86909c;
  }
  code {
    font-family: 'JetBrains Mono', 'Fira Code', Consolas, 'Courier New', monospace;
    font-size: 0.88em;
    background: #f2f3f5;
    border-radius: 3px;
    padding: 0.15em 0.3em;
  }
  pre {
    background: #1d2129;
    color: #e5e6eb;
    border-radius: 6px;
    padding: 1em;
    overflow-x: auto;
    margin: 0.8em 0;
  }
  pre code {
    background: none;
    padding: 0;
    font-size: 0.875em;
    color: inherit;
  }
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 0.8em 0;
  }
  th, td {
    border: 1px solid #e5e6eb;
    padding: 0.5em 0.75em;
    text-align: left;
  }
  th { background: #f2f3f5; font-weight: 600; }
  ul, ol { padding-left: 1.5em; margin: 0.6em 0; }
  li { margin: 0.25em 0; }
  hr { border: none; border-top: 1px solid #e5e6eb; margin: 1.2em 0; }
  img { max-width: 100%; border-radius: 4px; }
`;

const PROSE_CSS_DARK = `
  :host-context(.dark-mode) code { background: #333; }
  :host-context(.dark-mode) pre { background: #0e0e0e; color: #e5e6eb; }
  :host-context(.dark-mode) th { background: #262626; }
  :host-context(.dark-mode) th, :host-context(.dark-mode) td { border-color: #333; }
  :host-context(.dark-mode) blockquote { border-color: #404040; color: #929292; }
  :host-context(.dark-mode) hr { border-color: #333; }
`;

export function ShadowMarkdown({
  content,
  components,
  dompurifyConfig,
  style,
  className,
}: ShadowMarkdownProps) {
  const hostRef = useRef<HTMLDivElement>(null);
  const shadowRef = useRef<ShadowRoot | null>(null);
  const reactRootRef = useRef<Root | null>(null);
  const varsStyleRef = useRef<HTMLStyleElement | null>(null);
  const antdStylesRef = useRef<HTMLStyleElement | null>(null);

  // Sync antd CSS-in-JS styles that landed in document.head into the shadow root
  function syncAntdStyles(shadow: ShadowRoot) {
    const sheets = Array.from(document.head.querySelectorAll("style"));
    const antdText = sheets
      .filter(
        (s) =>
          s.getAttribute("data-css-hash") ||
          s.getAttribute("data-rc-order") ||
          s.textContent?.includes(".ant-") ||
          s.textContent?.includes(".qwenpaw-"),
      )
      .map((s) => s.textContent || "")
      .join("\n");

    if (!antdStylesRef.current) {
      antdStylesRef.current = document.createElement("style");
      shadow.insertBefore(antdStylesRef.current, shadow.firstChild);
    }
    antdStylesRef.current.textContent = antdText;
  }

  // Sync CSS custom properties so tokens work inside the shadow
  function syncVars(shadow: ShadowRoot) {
    if (!varsStyleRef.current) {
      varsStyleRef.current = document.createElement("style");
      shadow.insertBefore(varsStyleRef.current, shadow.firstChild);
    }
    varsStyleRef.current.textContent = buildHostVars();
  }

  // One-time shadow setup
  useLayoutEffect(() => {
    if (!hostRef.current || shadowRef.current) return;

    const shadow = hostRef.current.attachShadow({ mode: "open" });
    shadowRef.current = shadow;

    // Base prose styles (static)
    const proseStyle = document.createElement("style");
    proseStyle.textContent = PROSE_CSS + PROSE_CSS_DARK;
    shadow.appendChild(proseStyle);

    // Slots for synced styles (inserted before prose so they can be overridden)
    syncVars(shadow);
    syncAntdStyles(shadow);

    // Mount point for React
    const mountPoint = document.createElement("div");
    shadow.appendChild(mountPoint);
    reactRootRef.current = createRoot(mountPoint);
  }, []);

  // Re-render when content/components change
  useEffect(() => {
    reactRootRef.current?.render(
      <XMarkdown
        content={content}
        components={components}
        dompurifyConfig={dompurifyConfig}
      />,
    );
  });

  // Watch for new antd style injections + theme class changes
  useEffect(() => {
    const shadow = shadowRef.current;
    if (!shadow) return;

    // head observer for new style tags
    const headObs = new MutationObserver(() => syncAntdStyles(shadow));
    headObs.observe(document.head, { childList: true, subtree: false });

    // html attribute observer for dark-mode class / data-theme
    const htmlObs = new MutationObserver(() => syncVars(shadow));
    htmlObs.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class", "data-theme"],
    });

    return () => {
      headObs.disconnect();
      htmlObs.disconnect();
    };
  }, []);

  // Unmount React root on component unmount
  useEffect(() => {
    return () => {
      reactRootRef.current?.unmount();
    };
  }, []);

  return <div ref={hostRef} style={style} className={className} />;
}
