# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""Unit tests for the memory-distill tool plugin engine.

Ported from upstream PR agentscope-ai/QwenPaw#4171, adapted to the fork layout.

Module path: plugins/tool/memory-distill/memory_distill_tool.py
Loaded via importlib.util so the test runs without installing the plugin.
"""

import importlib.util
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from agentscope.tool._response import ToolResultState

_RECENT_DATE = (date.today() - timedelta(days=3)).isoformat()

# ---------------------------------------------------------------------------
# Load module under test without installing it
# ---------------------------------------------------------------------------

MODULE_PATH = (
    Path(__file__).resolve().parents[3]
    / "plugins"
    / "tool"
    / "memory-distill"
    / "memory_distill_tool.py"
)

_SPEC = importlib.util.spec_from_file_location(
    "memory_distill_tool", MODULE_PATH
)
assert _SPEC is not None and _SPEC.loader is not None, (
    f"Could not find memory_distill_tool at {MODULE_PATH}"
)
memory_distill_tool = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(memory_distill_tool)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _text(result) -> str:
    """Extract text from a ToolResponse (handles TextBlock or dict)."""
    block = result.content[0]
    return block["text"] if isinstance(block, dict) else block.text


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_distill_memory_rejects_non_workspace_dir(tmp_path):
    """Directory without MEMORY.md nor daily-notes dir is rejected."""
    result = await memory_distill_tool.distill_memory(
        working_dir=str(tmp_path),
        days=7,
        dry_run=True,
    )
    text = _text(result)
    assert "agent workspace" in text


@pytest.mark.asyncio
async def test_distill_memory_detects_new_titles_when_known_topics_exist(
    tmp_path,
):
    """New titles appear in preview; known topics are filtered out."""
    (tmp_path / "memory").mkdir()
    (tmp_path / "MEMORY.md").write_text(
        "# MEMORY\n\n- **Known Topic**: existing note\n",
        encoding="utf-8",
    )
    (tmp_path / "memory" / f"{_RECENT_DATE}.md").write_text(
        "# Daily\n\n## New Discovery\nFresh content here.\n\n"
        "## Known Topic\nShould be skipped.\n",
        encoding="utf-8",
    )
    result = await memory_distill_tool.distill_memory(
        working_dir=str(tmp_path),
        days=30,
        dry_run=True,
    )
    text = _text(result)
    assert "New Discovery" in text
    assert "Known Topic" not in text


@pytest.mark.asyncio
async def test_consolidate_memory_does_not_delete_workspace_png(tmp_path):
    """consolidate_memory must not touch files outside managed subdirs."""
    (tmp_path / "memory").mkdir()
    (tmp_path / "MEMORY.md").write_text("# MEMORY\n", encoding="utf-8")
    (tmp_path / "tool_results").mkdir()
    png = tmp_path / "keep.png"
    png.write_bytes(b"\x89PNG\r\n")

    await memory_distill_tool.consolidate_memory(
        working_dir=str(tmp_path),
        days=30,
        dry_run=False,
    )
    assert png.exists(), (
        "consolidate_memory must not delete workspace .png files"
    )


@pytest.mark.asyncio
async def test_distill_memory_dry_run_does_not_write(tmp_path):
    """dry_run=True must not modify MEMORY.md with new discoveries found."""
    (tmp_path / "memory").mkdir()
    mem = tmp_path / "MEMORY.md"
    mem.write_text("# MEMORY\n", encoding="utf-8")
    (tmp_path / "memory" / f"{_RECENT_DATE}.md").write_text(
        "# Daily\n\n## Brand New Thing\nsome content\n",
        encoding="utf-8",
    )
    before = mem.read_text(encoding="utf-8")

    result = await memory_distill_tool.distill_memory(
        working_dir=str(tmp_path),
        days=30,
        dry_run=True,
    )
    text = _text(result)

    # Preview must mention the new title
    assert "Brand New Thing" in text, (
        "dry_run preview must list new discoveries"
    )
    # File must be unchanged
    assert mem.read_text(encoding="utf-8") == before, (
        "dry_run=True must not write to MEMORY.md"
    )


# ---------------------------------------------------------------------------
# MISSING TESTS flagged by reviewer
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_distill_memory_sets_error_state_on_invalid_working_dir(
    tmp_path,
):
    """Empty directory must return state=ToolResultState.ERROR.

    Reviewer: assert result.state == ToolResultState.ERROR once fix applied.
    """
    result = await memory_distill_tool.distill_memory(
        working_dir=str(tmp_path),
        days=7,
        dry_run=True,
    )
    assert result.state == ToolResultState.ERROR, (
        f"Expected ERROR state for invalid workspace, got {result.state!r}"
    )
    # Sanity: the error message still describes the problem
    assert "agent workspace" in _text(result)


@pytest.mark.asyncio
async def test_consolidate_memory_uses_daily_memory_dir_from_config(
    tmp_path,
):
    """When _resolve_daily_dir_name() returns 'notes', consolidate_memory
    must look in <wd>/notes/ — not the hardcoded 'memory/'.
    """
    # Arrange: workspace with 'notes/' instead of 'memory/'
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    (tmp_path / "MEMORY.md").write_text("# MEMORY\n", encoding="utf-8")
    note_file = notes_dir / f"{_RECENT_DATE}.md"
    note_file.write_text(
        "# Daily\n\n## Config Resolution Topic\nsome custom content\n",
        encoding="utf-8",
    )

    # Act: patch _resolve_daily_dir_name to return 'notes' in the module
    with patch.object(
        memory_distill_tool,
        "_resolve_daily_dir_name",
        return_value="notes",
    ):
        result = await memory_distill_tool.consolidate_memory(
            working_dir=str(tmp_path),
            days=30,
            dry_run=True,
        )

    text = _text(result)
    # The pipeline ran successfully (no error state)
    assert result.state == ToolResultState.SUCCESS, (
        f"Expected SUCCESS, got {result.state!r}: {text}"
    )
    # Distill step must have found the note in notes/ and reported the topic
    found = (
        "Config Resolution Topic" in text
        or "1 new" in text
        or "new discovery" in text.lower()
    )
    assert found, (
        f"Expected distill step to find topic in notes/; got:\n{text}"
    )
