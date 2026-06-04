#!/usr/bin/env python3
"""Run release-grade ARK checks in one command."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Check:
    name: str
    command: list[str]
    display: str
    required_binary: str | None = None
    optional: bool = False


@dataclass(frozen=True)
class Result:
    status: str
    name: str
    detail: str = ""


def python_command(*args: str, display: str | None = None) -> Check:
    shown = display if display is not None else "python " + " ".join(args)
    return Check(
        name=shown,
        command=[sys.executable, *args],
        display=shown,
    )


def build_checks(require_claude: bool, skip_claude: bool) -> list[Check]:
    checks = [
        python_command("-m", "json.tool", ".claude-plugin/plugin.json"),
        python_command("-m", "json.tool", ".claude-plugin/marketplace.json"),
        python_command("-m", "json.tool", ".codex-plugin/plugin.json"),
        python_command(
            "scripts/ark-check.py",
            "--release",
            display="python scripts/ark-check.py --release",
        ),
        python_command("scripts/ark-smoke.py", display="python scripts/ark-smoke.py"),
        python_command(
            "scripts/ark-smoke.py",
            "--require-uv",
            display="python scripts/ark-smoke.py --require-uv",
        ),
        python_command(
            "scripts/ark-skill-smoke.py",
            display="python scripts/ark-skill-smoke.py",
        ),
        python_command(
            "scripts/ark-review-gate-smoke.py",
            display="python scripts/ark-review-gate-smoke.py",
        ),
        python_command(
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            display="python -m unittest discover -s tests",
        ),
        Check(
            name="uv ARK release self-check",
            command=["uv", "run", "python", "scripts/ark-check.py", "--release"],
            display="uv run python scripts/ark-check.py --release",
            required_binary="uv",
        ),
        Check(
            name="uv ARK smoke",
            command=["uv", "run", "python", "scripts/ark-smoke.py", "--require-uv"],
            display="uv run python scripts/ark-smoke.py --require-uv",
            required_binary="uv",
        ),
        Check(
            name="uv ARK skill smoke",
            command=["uv", "run", "python", "scripts/ark-skill-smoke.py"],
            display="uv run python scripts/ark-skill-smoke.py",
            required_binary="uv",
        ),
        Check(
            name="uv ARK review gate smoke",
            command=["uv", "run", "python", "scripts/ark-review-gate-smoke.py"],
            display="uv run python scripts/ark-review-gate-smoke.py",
            required_binary="uv",
        ),
        Check(
            name="uv unit tests",
            command=["uv", "run", "python", "-m", "unittest", "discover", "-s", "tests"],
            display="uv run python -m unittest discover -s tests",
            required_binary="uv",
        ),
    ]

    if not skip_claude:
        checks.append(
            Check(
                name="Claude plugin manifest validation",
                command=["claude", "plugin", "validate", "."],
                display="claude plugin validate .",
                required_binary="claude",
                optional=not require_claude,
            )
        )

    return checks


def list_checks(checks: list[Check]) -> None:
    print("ARK release checks:")
    for check in checks:
        suffix = " (optional)" if check.optional else ""
        print(f"- {check.display}{suffix}")


def run_check(check: Check) -> Result:
    if check.required_binary and shutil.which(check.required_binary) is None:
        detail = f"{check.required_binary} was not found on PATH"
        if check.optional:
            print(f"\n==> SKIP {check.name}: {detail}")
            return Result("SKIP", check.name, detail)
        print(f"\n==> FAIL {check.name}: {detail}")
        return Result("FAIL", check.name, detail)

    print(f"\n==> {check.name}")
    print(f"$ {check.display}")
    result = subprocess.run(check.command, cwd=ROOT, check=False)
    if result.returncode == 0:
        return Result("PASS", check.name)
    return Result("FAIL", check.name, f"exit code {result.returncode}")


def run_checks(checks: list[Check]) -> int:
    results: list[Result] = []
    for check in checks:
        result = run_check(check)
        results.append(result)
        if result.status == "FAIL":
            break

    print("\nSummary:")
    for result in results:
        detail = f" - {result.detail}" if result.detail else ""
        print(f"{result.status} {result.name}{detail}")

    failed = [result for result in results if result.status == "FAIL"]
    if failed:
        print("\nARK release check failed.")
        return 1

    print("\nARK release check passed.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run all release-grade ARK checks.")
    parser.add_argument(
        "--list",
        action="store_true",
        help="print the checks without running them",
    )
    claude_group = parser.add_mutually_exclusive_group()
    claude_group.add_argument(
        "--require-claude",
        action="store_true",
        help="fail when Claude Code CLI is not available",
    )
    claude_group.add_argument(
        "--skip-claude",
        action="store_true",
        help="do not run Claude plugin manifest validation",
    )
    args = parser.parse_args(argv)

    checks = build_checks(
        require_claude=args.require_claude,
        skip_claude=args.skip_claude,
    )
    if args.list:
        list_checks(checks)
        return 0
    return run_checks(checks)


if __name__ == "__main__":
    sys.exit(main())
