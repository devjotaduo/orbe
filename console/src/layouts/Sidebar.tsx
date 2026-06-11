import { Layout, Menu, Button, Modal, Input, Form, Tooltip, Badge } from "antd";
import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAppMessage } from "../hooks/useAppMessage";
import { SearchOutlined, PlusOutlined } from "@ant-design/icons";
import {
  SparkChatTabFill,
  SparkExitFullscreenLine,
  SparkSearchUserLine,
  SparkMenuExpandLine,
  SparkMenuFoldLine,
  SparkEmailLine,
} from "@agentscope-ai/icons";
import { clearAuthToken } from "../api/config";
import { authApi } from "../api/modules/auth";
import api from "../api";
import { useCodingMode } from "../stores/codingModeStore";
import styles from "./index.module.less";
import { useTheme } from "../contexts/ThemeContext";
import { useMenuItems, useRoutes } from "../plugins/registry/hooks";
import { Slot } from "../plugins/registry/Slot";
import {
  deriveOpenKeys,
  findMenuItem,
  flattenMenu,
  renderIcon,
  routeIdToPath,
  toAntdItems,
} from "./registry/adapter";
import type { FlatMenuEntry } from "./registry/adapter";
import type { MenuItem } from "../plugins/registry/types";
import type { ReactNode } from "react";

// ── Layout ────────────────────────────────────────────────────────────────

const { Sider } = Layout;
const MOBILE_SIDEBAR_QUERY = "(max-width: 768px)";

function isMobileSidebarViewport() {
  return (
    typeof window !== "undefined" &&
    typeof window.matchMedia === "function" &&
    window.matchMedia(MOBILE_SIDEBAR_QUERY).matches
  );
}
const INBOX_BADGE_POLLING_MS = 6000;

// ── Types ─────────────────────────────────────────────────────────────────

interface SidebarProps {
  /** Route id of the currently active page (e.g. "core.workspace"). */
  selectedKey: string;
  /** Controlled collapse state — driven by MainLayout so Header can toggle it too. */
  collapsed?: boolean;
  /** Sets collapse to a specific value (preferred over onToggleCollapse for programmatic use). */
  onSetCollapsed?: (val: boolean) => void;
  /** Controlled pixel width from MainLayout drag-to-resize (overrides internal calculation). */
  siderWidth?: number;
  /** mousedown handler for the drag handle, provided by MainLayout. */
  onDragStart?: (e: React.MouseEvent) => void;
}

// ── Sidebar ───────────────────────────────────────────────────────────────

export default function Sidebar({ selectedKey, collapsed: collapsedProp, onSetCollapsed, siderWidth: siderWidthProp, onDragStart }: SidebarProps) {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { message } = useAppMessage();
  const { isDark } = useTheme();
  // When coding mode is on, the sidebar "Chat" entry should land on /coding
  // (FileTree + Editor + Chat panel) rather than the bare Chat page.
  const { codingMode } = useCodingMode();
  const chatPath = codingMode ? "/coding" : "/chat";
  const [authEnabled, setAuthEnabled] = useState(false);
  const [accountModalOpen, setAccountModalOpen] = useState(false);
  const [accountLoading, setAccountLoading] = useState(false);
  const [accountForm] = Form.useForm();
  // collapsedProp from MainLayout is the source of truth; fall back to local state
  // for standalone use (e.g. tests that don't pass the prop).
  const [searchQuery, setSearchQuery] = useState('');
  const [collapsedLocal, setCollapsedLocal] = useState(false);
  const [recentSessions, setRecentSessions] = useState<Array<{ id: string; name: string }>>([]);
  const collapsed = collapsedProp ?? collapsedLocal;
  const setCollapsed = (val: boolean | ((prev: boolean) => boolean)) => {
    const next = typeof val === "function" ? val(collapsed) : val;
    if (onSetCollapsed) {
      onSetCollapsed(next);
    } else {
      setCollapsedLocal(next);
    }
  };
  const [isMobile, setIsMobile] = useState(isMobileSidebarViewport);
  const [hasInboxUnread, setHasInboxUnread] = useState(false);

  // Limpa o campo de busca sempre que sidebar colapsa.
  useEffect(() => {
    if (collapsed) setSearchQuery('');
  }, [collapsed]);

  // Menu + route snapshots from registry (builtin + plugin registrations merged).
  const agentMenu = useMenuItems("primary.agentScoped");
  const settingsMenu = useMenuItems("primary.settings");
  const routes = useRoutes();

  // ── Effects ──────────────────────────────────────────────────────────────

  useEffect(() => {
    authApi
      .getStatus()
      .then((res) => setAuthEnabled(res.enabled))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (
      typeof window === "undefined" ||
      typeof window.matchMedia !== "function"
    ) {
      return;
    }

    const mediaQuery = window.matchMedia(MOBILE_SIDEBAR_QUERY);
    const syncMobileSidebar = () => {
      setIsMobile(mediaQuery.matches);
      if (mediaQuery.matches) {
        setCollapsed(true);
        setSearchQuery('');
      }
    };

    syncMobileSidebar();
    mediaQuery.addEventListener("change", syncMobileSidebar);

    return () => {
      mediaQuery.removeEventListener("change", syncMobileSidebar);
    };
  }, []);
  useEffect(() => {
    const loadUnreadState = async () => {
      try {
        const [inboxRes, pushRes] = await Promise.all([
          api.getInboxEvents({
            unread_only: true,
            limit: 1,
          }),
          api.getPushMessages(),
        ]);
        const hasUnreadEvents = (inboxRes?.events?.length || 0) > 0;
        const hasPendingApprovals =
          (pushRes?.pending_approvals?.length || 0) > 0;
        setHasInboxUnread(hasUnreadEvents || hasPendingApprovals);
      } catch {
        // Keep previous state when polling fails.
      }
    };
    void loadUnreadState();
    const timer = window.setInterval(() => {
      void loadUnreadState();
    }, INBOX_BADGE_POLLING_MS);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    import('../pages/Chat/sessionApi').then(({ default: sessionApi }) => {
      sessionApi.getSessionList()
        .then(sessions => {
          setRecentSessions(
            sessions.slice(0, 15).map(s => ({ id: s.id, name: s.name || '' }))
          );
        })
        .catch(() => {});
    });
  }, []);

  // ── Search filter ─────────────────────────────────────────────────────────

  type AntdItem = NonNullable<import("antd").MenuProps["items"]>[number] & {
    children?: AntdItem[];
    label?: React.ReactNode;
  };

  /** Filtra recursivamente antd menu items pelo searchQuery (case-insensitive no label string). */
  const filterAntdItems = (items: AntdItem[], query: string): AntdItem[] => {
    if (!query) return items;
    const lower = query.toLowerCase();
    return items.reduce<AntdItem[]>((acc, item) => {
      const label = typeof item.label === 'string' ? item.label : '';
      const filteredChildren = item.children ? filterAntdItems(item.children, query) : undefined;
      if (label.toLowerCase().includes(lower) || (filteredChildren && filteredChildren.length > 0)) {
        acc.push(filteredChildren ? { ...item, children: filteredChildren } : item);
      }
      return acc;
    }, []);
  };

  // ── Adapter: convert MenuItem trees to antd, with inbox badge decoration.

  /** Wrap the inbox label with the unread-Badge while keeping all other labels intact. */
  const decorateLabel = (item: MenuItem, label: ReactNode): ReactNode => {
    if (item.id !== "core.inbox" || label == null) return label;
    return (
      <Badge dot={hasInboxUnread} color="rgba(255, 157, 77, 1)" offset={[5, 7]}>
        <span>{label}</span>
      </Badge>
    );
  };

  const agentMenuItems = useMemo(() => {
    const items = toAntdItems(agentMenu, { collapsed, decorateLabel }) as AntdItem[];
    return filterAntdItems(items, searchQuery);
    // hasInboxUnread closure inside decorateLabel — listed as dep explicitly.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [agentMenu, collapsed, hasInboxUnread, searchQuery]);

  const settingsMenuItems = useMemo(() => {
    const items = toAntdItems(settingsMenu, { collapsed }) as AntdItem[];
    return filterAntdItems(items, searchQuery);
  }, [settingsMenu, collapsed, searchQuery]);

  const derivedOpenKeys = useMemo(
    () => [...deriveOpenKeys(agentMenu), ...deriveOpenKeys(settingsMenu)],
    [agentMenu, settingsMenu],
  );
  const [openKeys, setOpenKeys] = useState<string[]>(() => [
    ...deriveOpenKeys(agentMenu),
    ...deriveOpenKeys(settingsMenu),
  ]);
  // Sync any newly registered group keys without closing user-toggled ones.
  useEffect(() => {
    setOpenKeys((prev) => {
      const next = derivedOpenKeys.filter((k) => !prev.includes(k));
      return next.length ? [...prev, ...next] : prev;
    });
  }, [derivedOpenKeys]);

  const handleOpenChange = (keys: string[]) => setOpenKeys(keys);

  const collapsedNavItems = useMemo(() => {
    // Sticky chat is its own carve-out (lives outside menu data — see builtinMenu.ts).
    const stickyChat: FlatMenuEntry = {
      key: "core.chat",
      icon: <SparkChatTabFill size={18} />,
      path: chatPath,
      label: t("nav.chat"),
    };
    // Inbox in collapsed mode shows a dot overlay on its icon (kept Sidebar-local
    // for the same reason as decorateLabel: live state isn't menu data).
    const decorateInboxIcon = (icon: ReactNode): ReactNode => (
      <span style={{ position: "relative", display: "inline-flex" }}>
        {icon ?? <SparkEmailLine size={18} />}
        {hasInboxUnread && (
          <span
            style={{
              position: "absolute",
              top: -1,
              right: -3,
              width: 6,
              height: 6,
              borderRadius: "50%",
              background: "rgba(255, 157, 77, 1)",
            }}
          />
        )}
      </span>
    );
    const flat = [
      stickyChat,
      ...flattenMenu(agentMenu, routes, 18),
      ...flattenMenu(settingsMenu, routes, 18),
    ];
    return flat.map((entry) =>
      entry.key === "core.inbox"
        ? { ...entry, icon: decorateInboxIcon(entry.icon) }
        : entry,
    );
  }, [agentMenu, settingsMenu, routes, chatPath, t, hasInboxUnread]);

  // ── Handlers ──────────────────────────────────────────────────────────────

  const handleMenuClick = (key: string, allItems: MenuItem[]) => {
    const item = findMenuItem(allItems, key);
    if (item?.href) {
      window.open(item.href, "_blank", "noopener,noreferrer");
      return;
    }
    const path = routeIdToPath(item?.route, routes);
    if (path) navigate(path);
  };

  const handleUpdateProfile = async (values: {
    currentPassword: string;
    newUsername?: string;
    newPassword?: string;
  }) => {
    const trimmedUsername = values.newUsername?.trim() || undefined;
    const trimmedPassword = values.newPassword?.trim() || undefined;

    if (values.newPassword && !trimmedPassword) {
      message.error(t("account.passwordEmpty"));
      return;
    }

    if (values.newUsername && !trimmedUsername) {
      message.error(t("account.usernameEmpty"));
      return;
    }

    if (!trimmedUsername && !trimmedPassword) {
      message.warning(t("account.nothingToUpdate"));
      return;
    }

    setAccountLoading(true);
    try {
      await authApi.updateProfile(
        values.currentPassword,
        trimmedUsername,
        trimmedPassword,
      );
      message.success(t("account.updateSuccess"));
      setAccountModalOpen(false);
      accountForm.resetFields();
      clearAuthToken();
      window.location.href = "/login";
    } catch (err: unknown) {
      const raw = err instanceof Error ? err.message : "";
      let msg = t("account.updateFailed");
      if (raw.includes("password is incorrect")) {
        msg = t("account.wrongPassword");
      } else if (raw.includes("Nothing to update")) {
        msg = t("account.nothingToUpdate");
      } else if (raw.includes("cannot be empty")) {
        msg = t("account.nothingToUpdate");
      } else if (raw) {
        msg = raw;
      }
      message.error(msg);
    } finally {
      setAccountLoading(false);
    }
  };

  // ── Render ────────────────────────────────────────────────────────────────

  // If MainLayout provides a controlled width (drag-to-resize), use it.
  // Otherwise fall back to the default AionUi values.
  const siderWidth = siderWidthProp !== undefined
    ? siderWidthProp
    : collapsed ? (isMobile ? 56 : 72) : 260;
  // Sticky chat is active when on /chat* or /coding routes.
  const isChatActive =
    selectedKey === "core.chat" || selectedKey === "core.coding";
  // `renderIcon` retained for tree-shaking awareness.
  void renderIcon;

  return (
    <>
    {isMobile && !collapsed && (
      <div
        className={styles.siderBackdrop}
        onClick={() => setCollapsed(true)}
        aria-hidden="true"
      />
    )}
    <Sider
      width={siderWidth}
      style={{ position: 'relative' }}
      className={`${styles.sider}${
        collapsed ? ` ${styles.siderCollapsed}` : ""
      }${isDark ? ` ${styles.siderDark}` : ""}${
        isMobile ? ` ${styles.siderMobileOverlay}` : ""
      }${isMobile && !collapsed ? ` ${styles.siderMobileOverlayOpen}` : ""}`}
    >
      {/* Drag-to-resize handle — AionUi canônico */}
      {!collapsed && !isMobile && onDragStart && (
        <div
          className={styles.siderResizeHandle}
          onMouseDown={onDragStart}
          aria-hidden="true"
        />
      )}
      {/* AionUi BrandHeader — 52px, logo square + app name */}
      {!collapsed && (
        <div className={styles.brandHeader}>
          <Slot name="header.logo" kind="replace">
            <div className={styles.brandLogoSquare}>
              <img
                src={isDark ? "/logo-dark.svg" : "/logo-light.svg"}
                alt="QwenPaw"
                className={styles.brandLogoImg}
              />
            </div>
          </Slot>
          <span className={styles.brandName}>QwenPaw</span>
        </div>
      )}


      {/* SiderToolbar — Nova Conversa, visível em modo expandido e colapsado */}
      <div className={styles.siderToolbar}>
        <button
          className={styles.newChatBtn}
          onClick={() => navigate('/chat')}
          title={t('nav.newChat', 'Nova Conversa')}
        >
          <PlusOutlined style={{ fontSize: 14 }} />
          {!collapsed && <span>{t('nav.newChat', 'Nova Conversa')}</span>}
        </button>
      </div>

            {collapsed ? (
        <nav className={styles.collapsedNav}>
          {collapsedNavItems.map((item) => {
            const isActive =
              item.key === "core.chat"
                ? isChatActive
                : selectedKey === item.key;
            return (
              <Tooltip
                key={item.key}
                title={item.label}
                placement="right"
                overlayInnerStyle={{
                  background: "rgba(0,0,0,0.75)",
                  color: "#fff",
                }}
              >
                <button
                  className={`${styles.collapsedNavItem} ${
                    isActive ? styles.collapsedNavItemActive : ""
                  }`}
                  onClick={() =>
                    item.href
                      ? window.open(item.href, "_blank", "noopener,noreferrer")
                      : navigate(item.path)
                  }
                >
                  {item.icon}
                </button>
              </Tooltip>
            );
          })}
        </nav>
      ) : (
        <>
          {/* Agent-scoped section: search + nav */}
          <div className={styles.agentScopedSection}>
            <div className={styles.siderSearch}>
              <Input
                prefix={<SearchOutlined style={{ fontSize: 12, opacity: 0.5 }} />}
                placeholder={t('nav.search', 'Search...')}
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                allowClear
                size="small"
              />
            </div>
            <Slot name="sider.top" kind="fill" />
            <Menu
              mode="inline"
              selectedKeys={[selectedKey]}
              openKeys={openKeys}
              onOpenChange={handleOpenChange}
              onClick={({ key }) => handleMenuClick(String(key), agentMenu)}
              items={agentMenuItems}
              theme={isDark ? "dark" : "light"}
              className={styles.sideMenu}
            />
          </div>

          {/* Global settings section */}
          <Menu
            mode="inline"
            selectedKeys={[selectedKey]}
            openKeys={openKeys}
            onOpenChange={handleOpenChange}
            onClick={({ key }) => handleMenuClick(String(key), settingsMenu)}
            items={settingsMenuItems}
            theme={isDark ? "dark" : "light"}
            className={styles.sideMenu}
          />
          <Slot name="sider.bottom" kind="fill" />
          {recentSessions.length > 0 && !searchQuery && (
            <div className={styles.recentSessions}>
              <div className={styles.recentSessionsLabel}>{t('nav.recentChats', 'Recent')}</div>
              <div className={styles.recentSessionsList}>
                {recentSessions.slice(0, 8).map(s => (
                  <button
                    key={s.id}
                    className={styles.recentSessionItem}
                    onClick={() => navigate(`/chat/${s.id}`)}
                    title={s.name}
                  >
                    <span className={styles.recentSessionName}>{s.name || t('nav.untitledChat', 'Untitled')}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {authEnabled && !collapsed && (
        <div className={styles.authActions}>
          <Button
            type="text"
            icon={<SparkSearchUserLine size={16} />}
            onClick={() => {
              accountForm.resetFields();
              setAccountModalOpen(true);
            }}
            block
            className={`${styles.authBtn} ${
              collapsed ? styles.authBtnCollapsed : ""
            }`}
          >
            {!collapsed && t("account.title")}
          </Button>
          <Button
            type="text"
            icon={<SparkExitFullscreenLine size={16} />}
            onClick={() => {
              clearAuthToken();
              window.location.href = "/login";
            }}
            block
            className={`${styles.authBtn} ${
              collapsed ? styles.authBtnCollapsed : ""
            }`}
          >
            {!collapsed && t("login.logout")}
          </Button>
        </div>
      )}

      <div className={styles.collapseToggleContainer}>
        <Button
          type="text"
          icon={
            collapsed ? (
              <SparkMenuExpandLine size={20} />
            ) : (
              <SparkMenuFoldLine size={20} />
            )
          }
          onClick={() => setCollapsed(!collapsed)}
          className={styles.collapseToggle}
        />
      </div>

      <Modal
        open={accountModalOpen}
        onCancel={() => setAccountModalOpen(false)}
        title={t("account.title")}
        footer={null}
        destroyOnHidden
        centered
      >
        <Form
          form={accountForm}
          layout="vertical"
          onFinish={handleUpdateProfile}
        >
          <Form.Item
            name="currentPassword"
            label={t("account.currentPassword")}
            rules={[
              { required: true, message: t("account.currentPasswordRequired") },
            ]}
          >
            <Input.Password />
          </Form.Item>
          <Form.Item name="newUsername" label={t("account.newUsername")}>
            <Input placeholder={t("account.newUsernamePlaceholder")} />
          </Form.Item>
          <Form.Item name="newPassword" label={t("account.newPassword")}>
            <Input.Password placeholder={t("account.newPasswordPlaceholder")} />
          </Form.Item>
          <Form.Item
            name="confirmPassword"
            label={t("account.confirmPassword")}
            dependencies={["newPassword"]}
            rules={[
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value && !getFieldValue("newPassword")) {
                    return Promise.resolve();
                  }
                  if (value === getFieldValue("newPassword")) {
                    return Promise.resolve();
                  }
                  return Promise.reject(
                    new Error(t("account.passwordMismatch")),
                  );
                },
              }),
            ]}
          >
            <Input.Password
              placeholder={t("account.confirmPasswordPlaceholder")}
            />
          </Form.Item>
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={accountLoading}
              block
            >
              {t("account.save")}
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </Sider>
    </>
  );
}
