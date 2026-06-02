#!/usr/bin/env python3
"""Smoke checks for ARK plugin assets without invoking Claude Code."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_UV_INIT = (
    "uv init --bare --name <distribution_name> --python <version> --build-backend hatch "
    "--no-workspace --vcs none --no-readme --no-pin-python"
)
ARTIFACTS = {
    "spec": "spec.template.md",
    "design": "design.template.md",
    "plan": "plan.template.md",
    "tasks": "tasks.template.md",
    "decisions": "decisions.template.md",
    "validation": "validation.template.md",
    "handoff": "handoff.template.md",
}
STAGE_TEMPLATES = ("stages.template.md", "stage-summary.template.md")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def smoke_manifest(errors: list[str]) -> None:
    plugin = json.loads(read(ROOT / ".claude-plugin" / "plugin.json"))
    marketplace = json.loads(read(ROOT / ".claude-plugin" / "marketplace.json"))
    if plugin["name"] != "ark":
        fail(errors, "plugin name must be ark")
    if marketplace["plugins"][0]["source"] != "./":
        fail(errors, "marketplace plugin source should remain ./")
    if plugin["version"] != marketplace["plugins"][0]["version"]:
        fail(errors, "plugin and marketplace plugin versions differ")


def smoke_artifact_templates(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="ark-smoke-") as tmp:
        root = Path(tmp)
        target = root / "docs" / "ark"
        target.mkdir(parents=True)
        for artifact, filename in ARTIFACTS.items():
            source = ROOT / "templates" / "artifacts" / filename
            destination = target / f"{artifact}.md"
            shutil.copyfile(source, destination)
            text = read(destination)
            for token in (
                f"<!-- ark-artifact: {artifact} -->",
                "<!-- schema-version: 1.1 -->",
                "<!-- last-updated: YYYY-MM-DD -->",
            ):
                if token not in text:
                    fail(errors, f"{destination.name} missing {token}")
            if not text.strip():
                fail(errors, f"{destination.name} is empty")
            if artifact == "tasks":
                for token in (
                    "功能/技术闭环",
                    "实施要点",
                    "建议验证方式",
                    "可与哪些任务合并验证",
                ):
                    if token not in text:
                        fail(errors, f"{destination.name} missing {token}")
            if artifact == "validation":
                for token in ("## 验证覆盖范围", "覆盖任务", "覆盖原因"):
                    if token not in text:
                        fail(errors, f"{destination.name} missing {token}")
            if artifact == "spec":
                for token in ("用户可观察能力", "不得写成文件/函数级实现步骤"):
                    if token not in text:
                        fail(errors, f"{destination.name} missing {token}")
            if artifact == "design":
                for token in ("## 技术闭环建议", "最小可运行闭环", "最小契约验证"):
                    if token not in text:
                        fail(errors, f"{destination.name} missing {token}")
            if artifact == "plan":
                for token in ("## 阶段推进路径", "建议 task 边界", "不建议拆分为"):
                    if token not in text:
                        fail(errors, f"{destination.name} missing {token}")
        if (root / "ark").exists():
            fail(errors, "smoke scaffold unexpectedly created nested ark directory")


def smoke_mode_b_boundaries(errors: list[str]) -> None:
    init_skill = read(ROOT / "skills" / "ark-init" / "SKILL.md")
    required = (
        "不得修改任何已有代码文件或项目配置",
        "`pyproject.toml`、`setup.py`、`setup.cfg` 等已有配置",
        "任何已有代码文件",
        "用户确认后才执行安装",
    )
    for token in required:
        if token not in init_skill:
            fail(errors, f"ark-init missing Mode B safety token: {token}")


def smoke_stage_templates(errors: list[str]) -> None:
    stage_dir = ROOT / "templates" / "stage"
    for filename in STAGE_TEMPLATES:
        path = stage_dir / filename
        if not path.exists():
            fail(errors, f"missing stage template: {filename}")
            continue
        text = read(path)
        if not text.strip():
            fail(errors, f"{filename} is empty")

    stages = read(stage_dir / "stages.template.md")
    for token in (
        "<!-- ark-artifact: stages -->",
        "## Current Stage",
        "## Stage History",
        "## Carryover Gates",
    ):
        if token not in stages:
            fail(errors, f"stages.template.md missing {token}")

    summary = read(stage_dir / "stage-summary.template.md")
    for token in (
        "<!-- ark-stage-summary: <stage-id> -->",
        "## 1. 阶段结论",
        "## 5. 可继承结论",
        "## 6. 不应继承的内容",
    ):
        if token not in summary:
            fail(errors, f"stage-summary.template.md missing {token}")


def smoke_init_contract(errors: list[str]) -> None:
    paths = (
        ROOT / "skills" / "ark-init" / "SKILL.md",
        ROOT / "skills" / "ark-init" / "references" / "project-bootstrap-guidelines.md",
        ROOT / "RELEASE.md",
    )
    for path in paths:
        text = read(path)
        if CANONICAL_UV_INIT not in text:
            fail(errors, f"{path.relative_to(ROOT)} missing canonical bare uv command")
        if "uv init --name <project_name>" in text:
            fail(errors, f"{path.relative_to(ROOT)} still documents non-bare uv command")


def smoke_optional_uv_bare(errors: list[str]) -> None:
    uv = shutil.which("uv")
    if uv is None:
        return

    with tempfile.TemporaryDirectory(prefix="ark-uv-smoke-") as tmp:
        root = Path(tmp)
        cache = root / "uv-cache"
        project = root / "project"
        project.mkdir()
        command = [
            uv,
            "init",
            "--bare",
            "--name",
            "smoke-pkg",
            "--python",
            "3.12",
            "--build-backend",
            "hatch",
            "--no-workspace",
            "--vcs",
            "none",
            "--no-readme",
            "--no-pin-python",
        ]
        env = os.environ.copy()
        env["UV_CACHE_DIR"] = str(cache)
        result = subprocess.run(
            command,
            cwd=project,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            fail(errors, "uv bare smoke failed: " + (result.stderr or result.stdout).strip())
            return

        pyproject = project / "pyproject.toml"
        if not pyproject.exists():
            fail(errors, "uv bare smoke did not create pyproject.toml")
            return
        text = read(pyproject)
        for token in ("[project.scripts]", "Hello from", "def main", "def hello"):
            if token in text:
                fail(errors, f"uv bare smoke pyproject contains sample token: {token}")
        unexpected_paths = (
            project / "src",
            project / "smoke_pkg",
            project / "smoke-pkg",
            project / "README.md",
        )
        for path in unexpected_paths:
            if path.exists():
                fail(errors, f"uv bare smoke unexpectedly created {path.name}")


def main() -> int:
    errors: list[str] = []
    smoke_manifest(errors)
    smoke_artifact_templates(errors)
    smoke_mode_b_boundaries(errors)
    smoke_stage_templates(errors)
    smoke_init_contract(errors)
    smoke_optional_uv_bare(errors)
    if errors:
        print("ARK smoke checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("ARK smoke checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
