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
        self.assertEqual(version, "1.0.7")
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
