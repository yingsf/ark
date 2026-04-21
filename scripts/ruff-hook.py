#!/usr/bin/env python3
"""ARK ruff hook: format + lint fix on the edited file."""
import json
import subprocess
import sys


def main() -> None:
    try:
        data = json.load(sys.stdin)
        file_path = data.get("tool_input", {}).get("file_path")
        if not file_path:
            return
        subprocess.run(["uv", "run", "ruff", "format", file_path], timeout=15)
        subprocess.run(["uv", "run", "ruff", "check", "--fix", file_path], timeout=15)
    except Exception:
        pass


if __name__ == "__main__":
    main()
