from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ArkAssetTests(unittest.TestCase):
    def test_versions_are_consistent(self) -> None:
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
        version = plugin["version"]
        self.assertEqual(version, "1.0.8")
        self.assertEqual(marketplace["metadata"]["version"], version)
        self.assertEqual(marketplace["plugins"][0]["version"], version)
        self.assertIn(f"version-{version}-blue.svg", (ROOT / "README.md").read_text())

    def test_init_uses_bare_uv_contract(self) -> None:
        canonical = (
            "uv init --bare --name <distribution_name> --python <version> "
            "--build-backend hatch --no-workspace --vcs none --no-readme --no-pin-python"
        )
        for rel in (
            "skills/ark-init/SKILL.md",
            "skills/ark-init/references/project-bootstrap-guidelines.md",
            "RELEASE.md",
        ):
            text = (ROOT / rel).read_text()
            self.assertIn(canonical, text)
            self.assertNotIn("uv init --name <project_name>", text)

    def test_package_name_placeholder_is_used_for_python_package(self) -> None:
        claude_template = (ROOT / "templates/project/CLAUDE.md.template").read_text()
        ruff_snippet = (ROOT / "templates/project/pyproject-ruff.snippet.toml").read_text()
        fallback = (ROOT / "skills/ark-init/references/fallback-templates.md").read_text()

        self.assertIn("包名为 `<package_name>`", claude_template)
        self.assertIn('known-first-party = ["<package_name>"]', ruff_snippet)
        self.assertIn('packages = ["src/<package_name>"]', fallback)
        self.assertNotIn('known-first-party = ["<project_name>"]', ruff_snippet)

    def test_stage_contract_assets_exist(self) -> None:
        stage_skill = (ROOT / "skills/ark-stage/SKILL.md").read_text()
        stages_template = (ROOT / "templates/stage/stages.template.md").read_text()
        summary_template = (ROOT / "templates/stage/stage-summary.template.md").read_text()

        for token in (
            "stage-status",
            "stage-close",
            "stage-open",
            "stage-transition",
            "closed-with-risk",
            "Carryover Gates",
            "docs/ark/archive/<stage-id>/",
            "preview",
            "用户确认",
            "项目级长期记忆",
            "当前仍有效决策索引",
            "不得生成空的 `decisions.md`",
            "不确定时默认保留",
            "superseded",
        ):
            self.assertIn(token, stage_skill)

        self.assertIn("<!-- ark-artifact: stages -->", stages_template)
        self.assertIn("## Carryover Gates", stages_template)
        self.assertIn("<!-- ark-stage-summary: <stage-id> -->", summary_template)
        self.assertIn("## 5. 可继承结论", summary_template)
        self.assertIn("继续保留到当前 `decisions.md`", summary_template)
        self.assertIn("标记为 `superseded` / 已替代", summary_template)

    def test_execution_efficiency_contract_assets_exist(self) -> None:
        tasks_skill = (ROOT / "skills/ark-tasks/SKILL.md").read_text()
        implement_skill = (ROOT / "skills/ark-implement/SKILL.md").read_text()
        validate_skill = (ROOT / "skills/ark-validate/SKILL.md").read_text()
        tasks_template = (ROOT / "templates/artifacts/tasks.template.md").read_text()
        validation_template = (
            ROOT / "templates/artifacts/validation.template.md"
        ).read_text()

        for token in (
            "功能交付单元",
            "可验证技术闭环",
            "实施要点",
            "默认只展开当前可执行窗口的 3-8 个任务",
        ):
            self.assertIn(token, tasks_skill)

        for token in (
            "显式功能 Batch 例外",
            "功能视角",
            "本次新增 / 改变的能力",
            "用户或调用方如何触发",
            "统一验证计划",
        ):
            self.assertIn(token, implement_skill)

        for token in (
            "验证覆盖范围",
            "覆盖任务",
            "覆盖原因",
            "不得用一条宽泛验证记录覆盖无关任务",
        ):
            self.assertIn(token, validate_skill)

        self.assertIn("功能/技术闭环", tasks_template)
        self.assertIn("可与哪些任务合并验证", tasks_template)
        self.assertIn("## 验证覆盖范围", validation_template)
        self.assertIn("覆盖原因", validation_template)

    def test_repository_checks_pass(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/ark-check.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_smoke_checks_pass(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/ark-smoke.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
