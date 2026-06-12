# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""Block Codex edits to secret-bearing file paths."""

import json
import os
import sys
from pathlib import Path


SECRET_NAMES = {
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    ".env.test",
}
SECRET_PARTS = (
    "secret",
    "secrets",
    "credential",
    "credentials",
    "keyring",
    "private_key",
    "id_rsa",
    "id_ed25519",
)


def _file_path(payload: dict) -> str:
    tool_input = payload.get("tool_input") or payload
    return str(tool_input.get("file_path") or "")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    raw_path = _file_path(payload)
    if not raw_path:
        return 0

    normalized = raw_path.replace("\\", "/").lower()
    name = Path(raw_path).name.lower()
    if (
        name in SECRET_NAMES
        or name.startswith(".env.")
        or any(part in normalized for part in SECRET_PARTS)
    ):
        sys.stderr.write(
            f"[secret-path-guard] BLOCKED edit to sensitive path: {raw_path}\n"
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
