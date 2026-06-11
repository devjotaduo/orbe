import { Suspense, useMemo, useState, useRef, useEffect, useCallback } from "react";
import { Layout, Spin } from "antd";
import { Routes, Route, useLocation, matchPath } from "react-router-dom";
import { useTranslation } from "react-i18next";
import Sidebar from "../Sidebar";
import Header from "../Header";
import ConsolePollService from "../../components/ConsolePollService";
import { ChunkErrorBoundary } from "../../components/ChunkErrorBoundary";
import { useSyncCodingMode } from "../../stores/useSyncCodingMode";
import styles from "../index.module.less";
import { useRoutes } from "../../plugins/registry/hooks";
import { Slot } from "../../plugins/registry/Slot";

const { Content } = Layout;

/**
 * Find the registered route whose path pattern matches the current URL.
 * Falls back to "core.chat" so the sidebar always has a sensible
 * highlight, mirroring the old `pathToKey` default.
 */
function pickSelectedKey(
  currentPath: string,
  routes: ReturnType<typeof useRoutes>,
): string {
  for (const r of routes) {
    if (matchPath({ path: r.path, end: r.path === "/" }, currentPath)) {
      return r.id;
    }
  }
  return "core.chat";
}

export default function MainLayout() {
  const { t } = useTranslation();
  const location = useLocation();
  const currentPath = location.pathname;
  const routes = useRoutes();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [siderWidth, setSiderWidth] = useState<number>(() => {
    try {
      return parseInt(localStorage.getItem('qwenpaw-sider-width') || '260', 10) || 260;
    } catch {
      return 260;
    }
  });

  // Keep a ref so the mouseup closure always reads the latest width.
  const siderWidthRef = useRef(siderWidth);
  useEffect(() => { siderWidthRef.current = siderWidth; }, [siderWidth]);

  // When sidebar collapses, record width=0; when it expands, restore saved/default.
  useEffect(() => {
    if (sidebarCollapsed) {
      setSiderWidth(0);
    } else {
      setSiderWidth(() => {
        try {
          return parseInt(localStorage.getItem('qwenpaw-sider-width') || '260', 10) || 260;
        } catch {
          return 260;
        }
      });
    }
  }, [sidebarCollapsed]);

  const isDragging = useRef(false);
  const dragStartX = useRef(0);
  const dragStartWidth = useRef(260);

  const handleDragStart = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    isDragging.current = true;
    dragStartX.current = e.clientX;
    dragStartWidth.current = siderWidthRef.current || 260;
    document.body.style.userSelect = 'none';
    document.body.style.cursor = 'col-resize';

    const onMove = (me: MouseEvent) => {
      if (!isDragging.current) return;
      const delta = me.clientX - dragStartX.current;
      const next = dragStartWidth.current + delta;
      if (next < 130) {
        setSidebarCollapsed(true);
        setSiderWidth(0);
      } else {
        setSidebarCollapsed(false);
        setSiderWidth(Math.min(Math.max(next, 160), 400));
      }
    };
    const onUp = () => {
      isDragging.current = false;
      document.body.style.userSelect = '';
      document.body.style.cursor = '';
      const finalWidth = siderWidthRef.current;
      if (finalWidth > 0) {
        try { localStorage.setItem('qwenpaw-sider-width', String(finalWidth)); } catch {}
      }
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    };
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  }, []);

  // Backend is the source of truth for Coding Mode state — refill the
  // in-memory store every time the selected agent changes.
  useSyncCodingMode();

  const selectedKey = useMemo(
    () => pickSelectedKey(currentPath, routes),
    [currentPath, routes],
  );

  return (
    <Layout className={styles.mainLayout}>
      <Header
        sidebarCollapsed={sidebarCollapsed}
        onToggleSidebar={() => setSidebarCollapsed((c) => !c)}
      />
      <Layout>
        <Sidebar
          selectedKey={selectedKey}
          collapsed={sidebarCollapsed}
          onSetCollapsed={setSidebarCollapsed}
          siderWidth={siderWidth}
          onDragStart={handleDragStart}
        />
        <Content className="page-container">
          <ConsolePollService />
          <Slot name="content.statusBar" kind="fill" />
          <div className="page-content">
            <ChunkErrorBoundary resetKey={currentPath}>
              <Suspense
                fallback={
                  <Spin
                    tip={t("common.loading")}
                    style={{ display: "block", margin: "20vh auto" }}
                  />
                }
              >
                <Routes>
                  {routes.map((r) => (
                    <Route key={r.id} path={r.path} element={<r.Component />} />
                  ))}
                </Routes>
              </Suspense>
            </ChunkErrorBoundary>
          </div>
        </Content>
      </Layout>
      <Slot name="overlay.global" kind="fill" />
    </Layout>
  );
}
