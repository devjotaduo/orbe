---
name: memory-distill
description: 使用此技能进行增量记忆蒸馏和整合。触发场景包括：用户要求"蒸馏记忆"、"整合笔记"、"清理 MEMORY.md"、"从每日笔记中发现新内容"，或定期记忆维护。使用标题差分（零 LLM 成本）检测每日笔记中的新信息并追加到 MEMORY.md。不要用于简单的记忆搜索（使用 memory_search）或直接写入单条笔记。
metadata:
  builtin_skill_version: "1.0"
  qwenpaw:
    emoji: "🧠"
---

# 记忆蒸馏

## 使用场景

- 用户要求"蒸馏"、"整合"或"清理"记忆
- Agent 检测到 MEMORY.md 与每日笔记之间存在重复信息
- 定期维护（每 7–15 天）
- 快速检查记忆状态

## 不适用场景

- 仅搜索现有记忆 → 使用 `memory_search`
- 直接写入单条笔记 → 直接更新 MEMORY.md 或每日笔记
- 需要 LLM 进行全量重新摘要 → 此工具进行文本差分，不是摘要

## 工具

| 函数 | 用途 | 常用参数 |
|:---|:---|---:|
| `distill_memory()` | 标题差分：扫描每日笔记，发现新内容 | `days=7`, `dry_run=True` |
| `consolidate_memory()` | 完整流程：蒸馏 → 归档 → 清理 → 审计 | `days=15`, `dry_run=True` |
| `inspect_memory()` | 快速健康检查 | — |

## 工作流程

1. `await inspect_memory()` — 检查当前状态
2. `await distill_memory(days=7, dry_run=True)` — 始终先预览
3. `await distill_memory(days=7, dry_run=False)` — 预览无误后执行
4. `await consolidate_memory(days=15, dry_run=False)` — 每约 15 天执行完整流程

## 算法

1. 从 MEMORY.md 提取**已知主题**：`**粗体标记**` 和 `###` 标题
2. 扫描每日笔记（`memory/YYYY-MM-DD.md`）中的 `##` 标题
3. 过滤 15+ 个常见模板标题（"Daily"、"Tasks"、"Todo" 等）
4. 仅将新发现追加到 `🔄 Auto Discovery` 部分
5. 原子写入（临时文件 + replace）— 崩溃时不会损坏 MEMORY.md

## 注意事项

- 始终从 `dry_run=True` 开始
- 每日笔记永不删除（仅由 `consolidate_memory` 归档）
- 零 LLM 成本 — 纯文本/标题差分
- 相比全量重新摘要减少约 92% 噪声
