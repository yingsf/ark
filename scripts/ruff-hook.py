#!/usr/bin/env python3
"""ARK ruff hook: format + lint fix on the edited file."""
import json
from pathlib import Path
import subprocess
import sys


def main() -> None:
    try:
        data = json.load(sys.stdin)
        file_path = data.get("tool_input", {}).get("file_path")
        if not file_path:
            return
        path = Path(file_path)
        if path.suffix not in {".py", ".pyi"}:
            return

        for command in (
            ["uv", "run", "ruff", "check", "--fix", file_path],
            ["uv", "run", "ruff", "format", file_path],
        ):
            result = subprocess.run(command, timeout=15, capture_output=True, text=True)
            if result.returncode != 0:
                sys.stderr.write(result.stderr or result.stdout)
    except Exception as exc:
        sys.stderr.write(f"ark ruff hook skipped: {exc}\n")
        pass


if __name__ == "__main__":
    main()
