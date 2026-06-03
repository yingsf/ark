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
        self.assertEqual(version, "1.0.11")
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
        comment_reference = (
            ROOT / "skills/ark-implement/references/comment-docstring-guidelines.md"
        ).read_text()
        batch_reference = (
            ROOT / "skills/ark-implement/references/batch-subagent-guidelines.md"
        ).read_text()
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
            "功能结果",
            "当前完成状态",
            "任务状态建议",
            "本次新增 / 改变的能力",
            "用户或调用方如何触发",
            "用户验收方式",
            "统一验证计划",
            "条件输出",
        ):
            self.assertIn(token, implement_skill)
        self.assertNotIn("功能视角", implement_skill)

        for token in (
            "fastchain-enhanced",
            "L0 无需补充",
            "变量后置三引号",
            "句末中文终止标点",
        ):
            self.assertIn(token, comment_reference)

        for token in (
            "显式功能 Batch",
            "统一验证计划",
            "write set",
            "Checkpoint 建议",
        ):
            self.assertIn(token, batch_reference)

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
        self.assertIn("阶段推进路径", validation_template)
        self.assertNotIn("阶段表", validation_template)

    def test_planning_granularity_contract_assets_exist(self) -> None:
        spec_skill = (ROOT / "skills/ark-spec/SKILL.md").read_text()
        design_skill = (ROOT / "skills/ark-design/SKILL.md").read_text()
        plan_skill = (ROOT / "skills/ark-plan/SKILL.md").read_text()
        spec_template = (ROOT / "templates/artifacts/spec.template.md").read_text()
        design_template = (ROOT / "templates/artifacts/design.template.md").read_text()
        plan_template = (ROOT / "templates/artifacts/plan.template.md").read_text()

        for token in (
            "用户可观察能力",
            "业务闭环",
            "不得写成文件、函数、类、配置项或实现步骤",
        ):
            self.assertIn(token, spec_skill)

        for token in (
            "技术闭环建议",
            "最小可运行闭环",
            "最小契约验证",
            "不建议拆成 task 的低层实现点",
        ):
            self.assertIn(token, design_skill)

        for token in (
            "阶段推进路径",
            "建议 task 边界",
            "不建议拆分为",
            "3-8 个当前窗口 task",
        ):
            self.assertIn(token, plan_skill)

        self.assertIn("不得写成文件/函数级实现步骤", spec_template)
        self.assertIn("## 技术闭环建议", design_template)
        self.assertIn("最小可运行闭环", design_template)
        self.assertIn("## 阶段推进路径", plan_template)
        self.assertIn("建议 task 边界", plan_template)
        self.assertIn("不建议拆分为", plan_template)

    def test_contract_fixtures_exist(self) -> None:
        fixture_dir = ROOT / "tests/fixtures/contracts"
        for name in (
            "plan-granularity",
            "implement-report",
            "validation-coverage",
        ):
            good = fixture_dir / f"{name}.good.md"
            bad = fixture_dir / f"{name}.bad.md"
            self.assertTrue(good.exists(), f"missing {good}")
            self.assertTrue(bad.exists(), f"missing {bad}")
            self.assertTrue(good.read_text().strip())
            self.assertTrue(bad.read_text().strip())

    def test_review_contract_assets_exist(self) -> None:
        review_skill = (ROOT / "skills/ark-review/SKILL.md").read_text()
        contract_reference = (
            ROOT / "skills/ark-review/references/contract-driven-python-review.md"
        ).read_text()
        craft_reference = (
            ROOT / "skills/ark-review/references/craftsmanship-review.md"
        ).read_text()
        recheck_reference = (
            ROOT / "skills/ark-review/references/recheck-guidelines.md"
        ).read_text()

        for token in (
            "深度契约驱动",
            "任务契约",
            "测试通过但业务语义不对",
            "fail-closed",
            "Craftsmanship 不等于 Finding",
            "## Findings",
            "## Craftsmanship",
            "## Verification",
            "## Open Questions",
            "## ARK Follow-up",
            "## Verdict",
        ):
            self.assertIn(token, review_skill)

        for rel in (
            "skills/ark-review/references/contract-driven-python-review.md",
            "skills/ark-review/references/craftsmanship-review.md",
            "skills/ark-review/references/recheck-guidelines.md",
        ):
            self.assertIn(f"${{CLAUDE_PLUGIN_ROOT}}/{rel}", review_skill)

        for token in (
            "契约识别",
            "跨层口径一致性",
            "fail-closed",
            "敏感信息",
            "测试通过但业务语义不对",
        ):
            self.assertIn(token, contract_reference)

        for token in (
            "Craftsmanship 不等于 Finding",
            "Upgrade",
            "Polish",
            "Keep",
            "Do now",
        ):
            self.assertIn(token, craft_reference)

        for token in (
            "上一轮 Findings",
            "修复前会失败",
            "修复后会通过",
            "破坏原有主路径",
        ):
            self.assertIn(token, recheck_reference)

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
