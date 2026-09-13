"""Decode a spilled Drive tool-result JSON into the local data tree.

The MCP Drive connector returns file bytes as base64 inside a JSON envelope, and
spills large responses to a file on disk. This turns either form into a real
file under ``data/``.

Usage:
    python tools/save_drive_result.py <result.json> <dest_path>
"""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path


def save(result_path: Path, dest: Path) -> int:
    envelope = json.loads(result_path.read_text(encoding="utf-8"))
    raw = base64.b64decode(envelope["content"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    return len(raw)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    written = save(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"{sys.argv[2]}: {written} bytes")


if __name__ == "__main__":
    main()
