#!/usr/bin/env python
"""Block accidental high-token Codex reads of generated or very large files."""

import json
import os
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
MAX_BYTES = 250_000
ALLOW_ENV = "QWENPAW_ALLOW_LARGE_CONTEXT"

BLOCKED_PARTS = {
    ".pytest_cache",
    "coverage",
    "dist",
    "htmlcov",
    "node_modules",
    "__pycache__",
}

BLOCKED_PREFIXES = (
    "ECC/",
    "console/dist/",
    "src/qwenpaw/console/",
    "src/qwenpaw/docs/",
    "website/dist/",
)

BLOCKED_NAMES = {
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "tokenizer.json",
    "vocab.json",
}


def _file_path(payload: dict) -> Path | None:
    tool_input = payload.get("tool_input") or payload
    raw = tool_input.get("file_path") or tool_input.get("path")
    return Path(raw).resolve() if raw else None


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def _should_block(path: Path) -> tuple[bool, str]:
    rel = _rel(path)
    parts = {part.lower() for part in path.parts}
    name = path.name.lower()

    if any(rel.startswith(prefix) for prefix in BLOCKED_PREFIXES):
        return True, "generated/vendor directory"
    if parts & BLOCKED_PARTS:
        return True, "cache/build/dependency directory"
    if name in BLOCKED_NAMES:
        return True, "large generated/lock file"
    try:
        if path.is_file() and path.stat().st_size > MAX_BYTES:
            return True, f"file larger than {MAX_BYTES} bytes"
    except OSError:
        return False, ""
    return False, ""


def main() -> int:
    if os.environ.get(ALLOW_ENV) == "1":
        return 0
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    path = _file_path(payload)
    if path is None:
        return 0

    blocked, reason = _should_block(path)
    if not blocked:
        return 0

    rel = _rel(path)
    sys.stderr.write(
        "[context-guard] BLOCKED high-token read: "
        f"{rel} ({reason}). Use rg/head/targeted extraction, or set "
        f"{ALLOW_ENV}=1 if the full file is explicitly needed.\n"
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
