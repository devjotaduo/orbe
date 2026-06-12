---
name: memory-distill
description: Use this skill for incremental memory distillation and consolidation. Triggers include any request to "distill memory", "consolidate notes", "clean up MEMORY.md", "find new discoveries in daily notes", or periodic memory maintenance. Uses title-diffing (zero LLM cost) to detect genuinely new information in daily notes and append it to MEMORY.md. Do NOT use for simple memory search (use memory_search) or for writing a single note directly.
metadata:
  builtin_skill_version: "1.0"
  qwenpaw:
    emoji: "🧠"
---

# Memory Distillation

## When to Use

- User asks to "distill", "consolidate", or "clean up" memory
- Agent detects duplicate information between MEMORY.md and daily notes
- Periodic maintenance (every 7–15 days)
- Quick health check on memory state

## When NOT to Use

- Only searching existing memory → use `memory_search`
- Writing a single note directly → update MEMORY.md or daily note directly
- Full re-summarization by LLM → this tool does text diffing, not summarization

## Tools

| Function | Purpose | Common args |
|:---|:---|---:|
| `distill_memory()` | Title-diffing: scan daily notes, find what is new | `days=7`, `dry_run=True` |
| `consolidate_memory()` | Full pipeline: distill → archive → clean → audit | `days=15`, `dry_run=True` |
| `inspect_memory()` | Quick health check | — |

## Workflow

1. `await inspect_memory()` — check current state
2. `await distill_memory(days=7, dry_run=True)` — always preview first
3. `await distill_memory(days=7, dry_run=False)` — apply if preview looks good
4. `await consolidate_memory(days=15, dry_run=False)` — full pipeline every ~15 days

## Algorithm

1. Extract **known topics** from MEMORY.md: `**bold markers**` and `###` headers
2. Scan `##` section titles from daily notes (`memory/YYYY-MM-DD.md`)
3. Filter 15+ common template titles ("Daily", "Tasks", "Todo", etc.)
4. Append only new discoveries to a `🔄 Auto Discovery` section
5. Atomic write (temp + replace) — never corrupts MEMORY.md on crash

## Notes

- Always start with `dry_run=True`
- Daily notes are never deleted (only archived by `consolidate_memory`)
- Zero LLM cost — pure text/title diffing
- ~92% noise reduction vs. full re-summarization
