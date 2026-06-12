# Memory Distillation Tool

A zero-LLM memory consolidation plugin for QwenPaw agents. Uses **title-diffing** to detect genuinely new information in daily notes and incrementally append it to `MEMORY.md` — achieving ~92% noise reduction compared to full re-summarization approaches.

## Overview

The plugin provides three tools:

| Tool | Purpose | Default args |
|---|---|---|
| `distill_memory` | Scan daily notes, diff against MEMORY.md, append only new discoveries | `days=7, dry_run=True` |
| `consolidate_memory` | Full pipeline: distill → archive old notes → clean temp files → audit | `days=15, dry_run=False` |
| `inspect_memory` | Health check: MEMORY.md size, topic count, recent notes | — |

All tools are **disabled by default** — enable them in the agent toolkit settings.

## How It Works

1. **Extract known topics** from `MEMORY.md`: `**bold markers**` and `### headers`
2. **Scan daily notes** (`memory/YYYY-MM-DD.md`) for `##` section titles
3. **Filter template noise**: 15+ common titles like "Daily", "Tasks", "Todo" are always skipped
4. **Diff**: only titles absent from known topics pass through
5. **Append** a `🔄 Auto Discovery` section to `MEMORY.md` (atomic write — temp file + replace)

## Usage

Always start with `dry_run=True`:

```python
# Step 1: preview what would be added
await distill_memory(days=7, dry_run=True)

# Step 2: apply if the preview looks good
await distill_memory(days=7, dry_run=False)

# Step 3: full pipeline every ~15 days
await consolidate_memory(days=15, dry_run=False)
```

## Configuration

The plugin respects the agent's `daily_memory_dir` config (default: `"memory"`). No API keys required.

Optional config fields (set via the plugin toolkit UI):
- `working_dir` — override the agent workspace root
- `default_days` — default lookback window (1–90, default 15)

## Requirements

No external dependencies. Uses only Python standard library + AgentScope.

## Notes

- Daily notes are **never deleted** — only archived to `archive/` by `consolidate_memory`
- `MEMORY.md` writes are atomic (temp file + `os.replace`) to prevent corruption on crash
- The plugin does not call any LLM — all processing is regex-based text diffing
