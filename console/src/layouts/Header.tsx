import { Layout, Space, Badge, Spin, Dropdown, Button as AntButton } from "antd";
import type { MenuProps } from "antd";
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  ArrowLeftOutlined,
  ArrowRightOutlined,
} from "@ant-design/icons";
import LanguageSwitcher from "../components/LanguageSwitcher/index";
import ThemeToggleButton from "../components/ThemeToggleButton";
import CodingModeToggle from "../components/CodingModeToggle";
import { useTranslation } from "react-i18next";
import { Button, Modal } from "@agentscope-ai/design";
import styles from "./index.module.less";
import api from "../api";
import { openExternalLink } from "../utils/openExternalLink";
import {
  GITHUB_URL,
  getDocsUrl,
  getFeatureDemosUrl,
  getFaqUrl,
  getReleaseNotesUrl,
  PYPI_URL,
  ONE_HOUR_MS,
  UPDATE_MD,
  isStableVersion,
  compareVersions,
} from "./constants";
import { useState, useEffect } from "react";
import { Slot } from "../plugins/registry/Slot";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  CopyOutlined,
  CheckOutlined,
  TagOutlined,
  GithubOutlined,
  FileTextOutlined,
  ReadOutlined,
  PlayCircleOutlined,
  QuestionCircleOutlined,
} from "@ant-design/icons";

const { Header: AntHeader } = Layout;

// ── Code block with copy button ───────────────────────────────────────────
function UpdateCodeBlock({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(code).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };
  return (
    <div className={styles.codeBlock}>
      <code className={styles.codeBlockInner}>{code}</code>
      <button
        className={`${styles.copyBtn} ${
          copied ? styles.copyBtnCopied : styles.copyBtnDefault
        }`}
        onClick={handleCopy}
        title="Copy"
      >
        {copied ? <CheckOutlined /> : <CopyOutlined />}
      </button>
    </div>
  );
}

interface HeaderProps {
  sidebarCollapsed?: boolean;
  onToggleSidebar?: () => void;
}

export default function Header({ sidebarCollapsed, onToggleSidebar }: HeaderProps) {
  const { t, i18n } = useTranslation();
  const [version, setVersion] = useState<string>("");
  const [latestVersion, setLatestVersion] = useState<string>("");
  const [updateModalOpen, setUpdateModalOpen] = useState(false);
  const [updateMarkdown, setUpdateMarkdown] = useState<string>("");

  useEffect(() => {
    api
      .getVersion()
      .then((res) => setVersion(res?.version ?? ""))
      .catch(() => {});
  }, []);

  useEffect(() => {
    fetch(PYPI_URL)
      .then((res) => res.json())
      .then((data) => {
        const releases = data?.releases ?? {};

        const versionsWithTime = Object.entries(releases)
          .filter(([v]) => isStableVersion(v))
          .map(([v, files]) => {
            const fileList = files as Array<{ upload_time_iso_8601?: string }>;
            const latestUpload = fileList
              .map((f) => f.upload_time_iso_8601)
              .filter(Boolean)
              .sort()
              .pop();
            return { version: v, uploadTime: latestUpload || "" };
          });

        versionsWithTime.sort((a, b) => {
          const timeDiff =
            new Date(b.uploadTime).getTime() - new Date(a.uploadTime).getTime();
          return timeDiff !== 0
            ? timeDiff
            : compareVersions(b.version, a.version);
        });

        const versions = versionsWithTime.map((v) => v.version);
        const latest = versions[0] ?? data?.info?.version ?? "";

        const releaseTime = versionsWithTime.find((v) => v.version === latest)
          ?.uploadTime;
        const isOldEnough =
          !!releaseTime &&
          new Date(releaseTime) <= new Date(Date.now() - ONE_HOUR_MS);

        if (isOldEnough) {
          setLatestVersion(latest);
        } else {
          setLatestVersion("");
        }
      })
      .catch(() => {});
  }, []);

  const hasUpdate =
    !!version && !!latestVersion && compareVersions(latestVersion, version) > 0;

  const handleOpenUpdateModal = () => {
    setUpdateMarkdown("");
    setUpdateModalOpen(true);
    const lang = i18n.language?.startsWith("zh")
      ? "zh"
      : i18n.language?.startsWith("ru")
      ? "ru"
      : "en";
    const faqLang = lang === "zh" ? "zh" : "en";
    const url = `https://qwenpaw.agentscope.io/docs/faq.${faqLang}.md`;
    fetch(url, { cache: "no-cache" })
      .then((res) => (res.ok ? res.text() : Promise.reject()))
      .then((text) => {
        const zhPattern = /###\s*QwenPaw如何更新[\s\S]*?(?=\n###|$)/;
        const enPattern = /###\s*How to update QwenPaw[\s\S]*?(?=\n###|$)/;
        const match = text.match(faqLang === "zh" ? zhPattern : enPattern);
        setUpdateMarkdown(
          match && lang !== "ru"
            ? match[0].trim()
            : UPDATE_MD[lang] ?? UPDATE_MD.en,
        );
      })
      .catch(() => {
        setUpdateMarkdown(UPDATE_MD[lang] ?? UPDATE_MD.en);
      });
  };

  const handleNavClick = (url: string) => {
    openExternalLink(url);
  };

  return (
    <>
      <AntHeader className={styles.header}>
        {/* AionUi TitleBar — left: collapse + nav arrows */}
        <div className={styles.titlebarLeft}>
          <AntButton
            type="text"
            size="small"
            icon={sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={onToggleSidebar}
            className={styles.titlebarBtn}
            aria-label="Toggle sidebar"
          />
          <AntButton
            type="text"
            size="small"
            icon={<ArrowLeftOutlined />}
            disabled
            className={styles.titlebarBtn}
            aria-label="Back"
          />
          <AntButton
            type="text"
            size="small"
            icon={<ArrowRightOutlined />}
            disabled
            className={styles.titlebarBtn}
            aria-label="Forward"
          />
        </div>

        {/* Center: version badge (subtle) */}
        <div className={styles.titlebarCenter}>
          {version && (
            <Badge
              dot={!!hasUpdate}
              color="rgba(255, 157, 77, 1)"
              offset={[4, 14]}
            >
              <span
                className={`${styles.versionBadge} ${
                  hasUpdate
                    ? styles.versionBadgeClickable
                    : styles.versionBadgeDefault
                }`}
                onClick={() => hasUpdate && handleOpenUpdateModal()}
              >
                v{version}
              </span>
            </Badge>
          )}
        </div>

        <Slot name="header.left" kind="fill" />
        <Space size={4}>
          <Slot name="header.right" kind="fill" />
          {/* AionUi right side: minimal — only essential toggles visible, rest in ⋯ */}
          <CodingModeToggle />
          <LanguageSwitcher />
          <ThemeToggleButton />
          <div className={styles.headerDivider} />
          <Dropdown
            trigger={["click"]}
            menu={{
              items: [
                {
                  key: "tutorial",
                  icon: <ReadOutlined />,
                  label: t("header.tutorial"),
                  onClick: () => handleNavClick(getDocsUrl(i18n.language)),
                },
                {
                  key: "featureDemos",
                  icon: <PlayCircleOutlined />,
                  label: t("header.featureDemos"),
                  onClick: () =>
                    handleNavClick(getFeatureDemosUrl(i18n.language)),
                },
                {
                  key: "changelog",
                  icon: <FileTextOutlined />,
                  label: t("header.changelog"),
                  onClick: () =>
                    handleNavClick(getReleaseNotesUrl(i18n.language)),
                },
                {
                  key: "faq",
                  icon: <QuestionCircleOutlined />,
                  label: t("header.faq"),
                  onClick: () => handleNavClick(getFaqUrl(i18n.language)),
                },
                { type: "divider" },
                {
                  key: "github",
                  icon: <GithubOutlined />,
                  label: t("header.github"),
                  onClick: () => handleNavClick(GITHUB_URL),
                },
              ] as MenuProps["items"],
            }}
          >
            <AntButton
              type="text"
              size="small"
              className={styles.titlebarBtn}
              aria-label="More options"
            >
              ···
            </AntButton>
          </Dropdown>
        </Space>
      </AntHeader>

      <Modal
        title={null}
        open={updateModalOpen}
        onCancel={() => setUpdateModalOpen(false)}
        footer={[
          <Button key="close" onClick={() => setUpdateModalOpen(false)}>
            {t("common.close")}
          </Button>,
          <Button
            key="releases"
            type="primary"
            className={styles.updateViewReleasesBtn}
            onClick={() => handleNavClick(getReleaseNotesUrl(i18n.language))}
          >
            {t("sidebar.updateModal.viewReleases")}
          </Button>,
        ]}
        width={960}
        className={styles.updateModal}
      >
        {/* Banner area */}
        <div className={styles.updateModalBanner}>
          <div className={styles.updateModalBannerLeft}>
            <span className={styles.updateModalVersionTag}>
              <TagOutlined />
              Version {latestVersion || version}
            </span>
            <div className={styles.updateModalBannerTitle}>
              {t("sidebar.updateModal.title", {
                version: latestVersion || version,
              })}
            </div>
          </div>
        </div>

        {/* Markdown content */}
        <div className={styles.updateModalBody}>
          {updateMarkdown ? (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                a({ href, children, ...props }: any) {
                  return (
                    <a
                      {...props}
                      href={href}
                      onClick={(e) => {
                        e.preventDefault();
                        if (href) handleNavClick(href);
                      }}
                      style={{ cursor: "pointer" }}
                    >
                      {children}
                    </a>
                  );
                },
                code({ node, className, children, ...props }: any) {
                  const match = /language-(\w+)/.exec(className || "");
                  const isBlock =
                    node?.position?.start?.line !== node?.position?.end?.line ||
                    match;
                  return isBlock ? (
                    <UpdateCodeBlock
                      code={String(children).replace(/\n$/, "")}
                    />
                  ) : (
                    <code className={styles.codeInline} {...props}>
                      {children}
                    </code>
                  );
                },
              }}
            >
              {updateMarkdown}
            </ReactMarkdown>
          ) : (
            <div className={styles.updateModalSpinWrapper}>
              <Spin />
            </div>
          )}
        </div>
      </Modal>
    </>
  );
}
