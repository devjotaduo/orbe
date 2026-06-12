# -*- coding: utf-8 -*-
# pylint: disable=too-many-locals,too-many-branches,too-many-statements
"""Memory Distillation Tool — title-diffing engine.

Three tools (disabled by default — opt-in via the plugin toolkit):
  - distill_memory      : diff daily notes against MEMORY.md; append only new.
  - consolidate_memory  : full pipeline — distill + archive + clean + audit.
  - inspect_memory      : health-check MEMORY.md and daily notes.

Zero LLM calls — pure text/title diffing (~92% noise reduction per upstream PR
agentscope-ai/QwenPaw#4171).
"""

import logging
import os
import re
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional, Set

from agentscope.message import TextBlock
from agentscope.tool import ToolResponse
from agentscope.tool._response import ToolResultState

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Section titles that appear in almost every daily-note template — skip them
# when diffing so they never show up as "new discoveries".
_KNOWN_TEMPLATE_TITLES: Set[str] = {
    "daily",
    "today",
    "tasks",
    "task",
    "notes",
    "note",
    "todo",
    "done",
    "completed",
    "in progress",
    "blocked",
    "meetings",
    "meeting",
    "agenda",
    "follow up",
    "follow-up",
    "action items",
    "action item",
    "links",
    "references",
    "misc",
    "miscellaneous",
    "other",
    "thoughts",
    "ideas",
    "idea",
    "journal",
    "log",
    "scratch",
    "scratch pad",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_daily_dir_name() -> str:
    """Resolve the daily-notes subdir name from the current agent config.

    Falls back to ``"memory"`` (the upstream default and the value used by
    ``AgentMdManager``) when no agent context/config is available.
    """
    try:
        from qwenpaw.app.agent_context import (
            get_current_agent_id,
        )
        from qwenpaw.config.config import (
            load_agent_config,
        )

        agent_id = get_current_agent_id()
        if agent_id:
            cfg = load_agent_config(agent_id)
            name = getattr(cfg.running, "daily_memory_dir", None)
            if name:
                return str(name)
    except Exception:  # pragma: no cover — best-effort, never block the tool
        pass
    return "memory"


def _resolve_working_dir(working_dir: Optional[str] = None) -> Path:
    """Return a validated Path for the agent workspace.

    Validation: the directory must contain either ``MEMORY.md`` or the
    configured daily-notes subdirectory (resolved via
    ``_resolve_daily_dir_name``).
    This avoids operating on arbitrary filesystem paths.

    Raises:
        ValueError: if the path does not look like an agent workspace.
    """
    if working_dir:
        wd = Path(working_dir).expanduser().resolve()
    else:
        wd = Path(os.getcwd()).resolve()

    daily_dir_name = _resolve_daily_dir_name()
    memory_file = wd / "MEMORY.md"
    daily_dir = wd / daily_dir_name

    if not memory_file.exists() and not daily_dir.exists():
        raise ValueError(
            f"working_dir '{wd}' does not look like an agent workspace "
            f"containing {daily_dir_name}/ or MEMORY.md. "
            "Please pass the correct agent working directory.",
        )
    return wd


def _read_file(path: Path) -> str:
    """Read a text file with UTF-8 → latin-1 fallback."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def _known_topics_in_memory(memory_text: str) -> Set[str]:
    """Extract known-topic tokens from MEMORY.md.

    Recognises:
    - ``**bold text**`` markers (inline knowledge topics)
    - ``### Section headers``
    """
    topics: Set[str] = set()
    # bold markers: **topic**
    for match in re.finditer(r"\*\*([^*]+)\*\*", memory_text):
        topics.add(match.group(1).strip().lower())
    # ### headers
    for match in re.finditer(r"^#{1,6}\s+(.+)$", memory_text, re.MULTILINE):
        topics.add(match.group(1).strip().lower())
    return topics


def _daily_note_titles(note_text: str) -> List[str]:
    """Extract ``##`` section titles from a daily note."""
    titles = []
    for match in re.finditer(r"^##\s+(.+)$", note_text, re.MULTILINE):
        title = match.group(1).strip()
        if title.lower() not in _KNOWN_TEMPLATE_TITLES:
            titles.append(title)
    return titles


def _snippet_for_title(note_text: str, title: str) -> str:
    """Return first non-empty line under *title* (up to 120 chars)."""
    in_section = False
    for line in note_text.splitlines():
        if re.match(r"^##\s+" + re.escape(title) + r"\s*$", line):
            in_section = True
            continue
        if in_section:
            if line.startswith("##"):
                break
            stripped = line.strip()
            if stripped:
                return stripped[:120]
    return ""


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


async def distill_memory(
    working_dir: Optional[str] = None,
    days: int = 7,
    dry_run: bool = True,
) -> ToolResponse:
    """Distill daily notes into MEMORY.md using title-diffing.

    Scans the last *days* daily notes, finds section titles not yet present in
    ``MEMORY.md``, and appends them under a ``🔄 Auto Discovery`` section.

    Args:
        working_dir: Agent workspace root (defaults to cwd).
        days: How many days back to scan.
        dry_run: If True, return a preview without writing anything.

    Returns:
        ToolResponse with new discoveries report (or a dry-run preview).
    """
    try:
        wd = _resolve_working_dir(working_dir)
    except ValueError as exc:
        return ToolResponse(
            content=[TextBlock(type="text", text=str(exc))],
            state=ToolResultState.ERROR,
        )

    memory_file = wd / "MEMORY.md"
    daily_dir = wd / _resolve_daily_dir_name()

    # Read existing MEMORY.md (may not exist yet)
    memory_text = _read_file(memory_file) if memory_file.exists() else ""
    known_topics = _known_topics_in_memory(memory_text)

    # Scan daily notes for the last `days` days
    today = date.today()
    new_discoveries: List[tuple] = []  # (title, snippet, note_date)

    for delta in range(days):
        note_date = today - timedelta(days=delta)
        note_path = daily_dir / f"{note_date.isoformat()}.md"
        if not note_path.exists():
            continue
        note_text = _read_file(note_path)
        for title in _daily_note_titles(note_text):
            if title.lower() not in known_topics:
                snippet = _snippet_for_title(note_text, title)
                new_discoveries.append((title, snippet, note_date))
                # Add to known so duplicates across notes don't double-appear
                known_topics.add(title.lower())

    if not new_discoveries:
        msg = (
            f"[distill_memory] No new discoveries in the last {days} days "
            "(all titles already present in MEMORY.md or are template titles)."
        )
        return ToolResponse(content=[TextBlock(type="text", text=msg)])

    # Build the section to append
    lines = [
        "",
        "## 🔄 Auto Discovery",
        f"_Distilled {date.today().isoformat()} — "
        f"{len(new_discoveries)} new item(s) from the last {days} day(s)_",
        "",
    ]
    for title, snippet, note_date in new_discoveries:
        line = f"- 🔍 **{title}**"
        if snippet:
            line += f" — {snippet}"
        line += f" _(from {note_date.isoformat()})_"
        lines.append(line)
    lines.append("")
    section_text = "\n".join(lines)

    if dry_run:
        n = len(new_discoveries)
        preview = (
            f"[distill_memory] DRY RUN — {n} new discovery(ies) "
            f"would be appended to MEMORY.md:\n{section_text}"
        )
        return ToolResponse(content=[TextBlock(type="text", text=preview)])

    # Atomic append: write to .tmp then os.replace (avoids half-written
    # MEMORY.md on crash — spec §7).
    existing = _read_file(memory_file) if memory_file.exists() else ""
    new_content = existing + section_text
    tmp_path = memory_file.with_suffix(".tmp")
    try:
        tmp_path.write_text(new_content, encoding="utf-8")
        os.replace(str(tmp_path), str(memory_file))
    finally:
        tmp_path.unlink(missing_ok=True)

    result = (
        f"[distill_memory] Appended {len(new_discoveries)} new discovery(ies) "
        f"to MEMORY.md.\n{section_text}"
    )
    return ToolResponse(content=[TextBlock(type="text", text=result)])


async def consolidate_memory(
    working_dir: Optional[str] = None,
    days: int = 15,
    dry_run: bool = False,
) -> ToolResponse:
    """Run the full memory consolidation pipeline.

    Steps:
    1. Distill new discoveries into MEMORY.md.
    2. Archive daily notes older than *days* days into ``archive/``.
    3. Clean stale ``.txt`` files from ``tool_results/``.
    4. Audit MEMORY.md health (size, section count).

    Args:
        working_dir: Agent workspace root (defaults to cwd).
        days: Lookback window for distillation and archival cutoff.
        dry_run: If True, report what would happen without making changes.

    Returns:
        ToolResponse with a consolidated pipeline report.
    """
    try:
        wd = _resolve_working_dir(working_dir)
    except ValueError as exc:
        return ToolResponse(
            content=[TextBlock(type="text", text=str(exc))],
            state=ToolResultState.ERROR,
        )

    daily_dir_name = _resolve_daily_dir_name()
    daily_dir = wd / daily_dir_name
    archive_dir = wd / "archive"
    report_lines: List[str] = ["[consolidate_memory] Pipeline report:"]

    # --- Step 1: Distill ---
    distill_result = await distill_memory(
        working_dir=str(wd),
        days=days,
        dry_run=dry_run,
    )
    distill_text = (
        distill_result.content[0].text if distill_result.content else ""
    )
    first_line = (distill_text.splitlines() or ["(no output)"])[0]
    report_lines.append(f"  [1/4 distill] {first_line}")

    # --- Step 2: Archive old daily notes ---
    archived = 0
    cutoff = date.today() - timedelta(days=days)
    if daily_dir.exists():
        if not dry_run and not archive_dir.exists():
            archive_dir.mkdir(parents=True)
        for note_path in sorted(daily_dir.glob("*.md")):
            try:
                note_date = date.fromisoformat(note_path.stem)
            except ValueError:
                continue
            if note_date < cutoff:
                dest = archive_dir / note_path.name
                if not dry_run:
                    note_path.rename(dest)
                archived += 1
    report_lines.append(
        f"  [2/4 archive] {'Would archive' if dry_run else 'Archived'} "
        f"{archived} daily note(s) older than {cutoff.isoformat()}.",
    )

    # --- Step 3: Clean stale tool_results/*.txt ---
    cleaned = 0
    tool_results_dir = wd / "tool_results"
    if tool_results_dir.exists():
        for fpath in tool_results_dir.glob("*.txt"):
            if fpath.is_file():
                if not dry_run:
                    fpath.unlink()
                cleaned += 1
    report_lines.append(
        f"  [3/4 clean] {'Would remove' if dry_run else 'Removed'} "
        f"{cleaned} stale .txt file(s) from tool_results/.",
    )

    # --- Step 4: Audit MEMORY.md health ---
    memory_file = wd / "MEMORY.md"
    if memory_file.exists():
        mem_text = _read_file(memory_file)
        size_kb = round(memory_file.stat().st_size / 1024, 1)
        topic_count = len(_known_topics_in_memory(mem_text))
        section_count = len(re.findall(r"^#{1,3}\s+", mem_text, re.MULTILINE))
        audit = (
            f"MEMORY.md: {size_kb} KB, "
            f"~{topic_count} known topic(s), "
            f"{section_count} section(s)."
        )
    else:
        audit = "MEMORY.md not found — will be created on next distill."
    report_lines.append(f"  [4/4 audit] {audit}")

    report = "\n".join(report_lines)
    return ToolResponse(content=[TextBlock(type="text", text=report)])


async def inspect_memory(
    working_dir: Optional[str] = None,
) -> ToolResponse:
    """Inspect MEMORY.md and daily notes health.

    Returns a summary of MEMORY.md size, topic count, number of daily notes,
    and the most recently modified note.

    Args:
        working_dir: Agent workspace root (defaults to cwd).

    Returns:
        ToolResponse with a health-check report.
    """
    try:
        wd = _resolve_working_dir(working_dir)
    except ValueError as exc:
        return ToolResponse(
            content=[TextBlock(type="text", text=str(exc))],
            state=ToolResultState.ERROR,
        )

    daily_dir_name = _resolve_daily_dir_name()
    daily_dir = wd / daily_dir_name
    memory_file = wd / "MEMORY.md"

    lines: List[str] = ["[inspect_memory] Memory health report:"]

    # MEMORY.md stats
    if memory_file.exists():
        mem_text = _read_file(memory_file)
        size_kb = round(memory_file.stat().st_size / 1024, 1)
        topic_count = len(_known_topics_in_memory(mem_text))
        section_count = len(re.findall(r"^#{1,3}\s+", mem_text, re.MULTILINE))
        lines.append(
            f"  MEMORY.md: {size_kb} KB · "
            f"~{topic_count} known topic(s) · "
            f"{section_count} section(s)",
        )
    else:
        lines.append("  MEMORY.md: not found")

    # Daily notes stats
    if daily_dir.exists():
        note_files = sorted(daily_dir.glob("*.md"), reverse=True)
        lines.append(f"  {daily_dir_name}/: {len(note_files)} daily note(s)")
        if note_files:
            lines.append(f"  Most recent: {note_files[0].name}")
    else:
        lines.append(f"  {daily_dir_name}/: directory not found")

    report = "\n".join(lines)
    return ToolResponse(content=[TextBlock(type="text", text=report)])
