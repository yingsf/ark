#!/usr/bin/env python3
"""Lightweight repository checks for ARK plugin assets."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def check_versions(errors: list[str]) -> None:
    plugin = json.loads(read(ROOT / ".claude-plugin" / "plugin.json"))
    marketplace = json.loads(read(ROOT / ".claude-plugin" / "marketplace.json"))
    version = plugin.get("version")

    if marketplace.get("metadata", {}).get("version") != version:
        fail(errors, "marketplace metadata version does not match plugin.json")

    for item in marketplace.get("plugins", []):
        if item.get("name") == plugin.get("name") and item.get("version") != version:
            fail(errors, "marketplace plugin version does not match plugin.json")

    readme = read(ROOT / "README.md")
    badge = f"version-{version}-blue.svg"
    if badge not in readme:
        fail(errors, f"README version badge does not contain {badge}")


def check_artifact_templates(errors: list[str]) -> None:
    artifact_dir = ROOT / "templates" / "artifacts"
    expected = {
        "spec": "spec.template.md",
        "design": "design.template.md",
        "plan": "plan.template.md",
        "tasks": "tasks.template.md",
        "decisions": "decisions.template.md",
        "validation": "validation.template.md",
        "handoff": "handoff.template.md",
    }

    for artifact, filename in expected.items():
        path = artifact_dir / filename
        if not path.exists():
            fail(errors, f"missing artifact template: {path.relative_to(ROOT)}")
            continue
        text = read(path)
        if f"<!-- ark-artifact: {artifact} -->" not in text:
            fail(errors, f"{filename} missing ark-artifact header")
        if "<!-- schema-version: 1.1 -->" not in text:
            fail(errors, f"{filename} missing schema-version 1.1")
        if "<!-- last-updated: YYYY-MM-DD -->" not in text:
            fail(errors, f"{filename} missing last-updated placeholder")

    tasks = read(artifact_dir / "tasks.template.md")
    for token in ("Ready for validation", "完成后可观察结果", "外部依据"):
        if token not in tasks:
            fail(errors, f"tasks.template.md missing {token}")
    if "## Last updated" in tasks:
        fail(errors, "tasks.template.md should use header last-updated only")

    spec = read(artifact_dir / "spec.template.md")
    if "核心命题与不变量" not in spec:
        fail(errors, "spec.template.md missing core proposition section")


def check_ruff_snippet(errors: list[str]) -> None:
    snippet = read(ROOT / "templates" / "project" / "pyproject-ruff.snippet.toml")
    for rule in ("RUF001", "RUF002", "RUF003"):
        if rule not in snippet:
            fail(errors, f"Ruff snippet missing {rule} ignore")


def check_skill_references(errors: list[str]) -> None:
    pattern = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)")
    for path in (ROOT / "skills").rglob("SKILL.md"):
        text = read(path)
        for rel in pattern.findall(text):
            target = ROOT / rel
            if not target.exists():
                fail(
                    errors,
                    f"{path.relative_to(ROOT)} references missing path: {rel}",
                )


def check_workflow_tokens(errors: list[str]) -> None:
    required = {
        "skills/ark-implement/SKILL.md": [
            "前序结论吸收",
            "Ready for validation",
            "Checkpoint 建议",
            "fastchain-enhanced",
            "注释详细度分级",
            "句末中文终止标点",
        ],
        "skills/ark-validate/SKILL.md": [
            "Ready for validation → Done",
            "Checkpoint 建议",
        ],
        "skills/ark-review/SKILL.md": [
            "fastchain-enhanced",
            "注释详细度分级",
            "句末中文终止标点",
            "尾随解释注释",
        ],
        "skills/ark-sync/SKILL.md": [
            "变更传播判断",
            "核心命题与不变量",
        ],
        "skills/ark-next/SKILL.md": [
            "当前最可信",
            "用户需提供的信息",
        ],
        "skills/ark-handoff/SKILL.md": [
            "下一次必须继承的结论",
        ],
        "rules/python-backend-conventions.md": [
            "fastchain-enhanced",
            "L0 无需补充",
            "L2 fastchain-enhanced",
            "中文标点规则",
            "解释性尾随注释",
        ],
        "templates/project/CLAUDE.md.template": [
            "注释详细度：fastchain-enhanced",
            "句末中文终止标点",
            "解释性尾随注释",
        ],
        "skills/ark-init/references/fallback-templates.md": [
            "注释详细度：fastchain-enhanced",
            "句末中文终止标点",
            "解释性尾随注释",
        ],
    }

    for rel, tokens in required.items():
        text = read(ROOT / rel)
        for token in tokens:
            if token not in text:
                fail(errors, f"{rel} missing workflow token: {token}")


def main() -> int:
    errors: list[str] = []
    check_versions(errors)
    check_artifact_templates(errors)
    check_ruff_snippet(errors)
    check_skill_references(errors)
    check_workflow_tokens(errors)

    if errors:
        print("ARK self-check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("ARK self-check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
