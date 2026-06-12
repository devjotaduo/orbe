#!/usr/bin/env python
"""Run local Prettier after Codex edits, constrained to this repository."""

import json
import os
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
FORMATTABLE_EXTS = {".ts", ".tsx", ".js", ".jsx", ".css", ".json"}


def _file_path(payload: dict) -> Path | None:
    tool_input = payload.get("tool_input") or payload
    raw = tool_input.get("file_path")
    return Path(raw).resolve() if raw else None


def _inside_repo(path: Path) -> bool:
    try:
        path.relative_to(REPO)
        return True
    except ValueError:
        return False


def _prettier_cwd(path: Path) -> Path:
    console = REPO / "console"
    try:
        path.relative_to(console)
        return console
    except ValueError:
        return REPO


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    path = _file_path(payload)
    if path is None or path.suffix.lower() not in FORMATTABLE_EXTS:
        return 0
    if not _inside_repo(path) or not path.exists() or not path.is_file():
        return 0

    cmd = ["npx", "--no-install", "prettier", "--write", "--cache", str(path)]
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(_prettier_cwd(path)),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        sys.stderr.write(f"[prettier-hook] skipped: {exc}\n")
        return 0

    if completed.returncode != 0:
        sys.stderr.write(f"[prettier-hook] prettier failed: {completed.stderr.strip()}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
