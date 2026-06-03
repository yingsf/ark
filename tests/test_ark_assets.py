from __future__ import annotations

import json
import re
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
        self.assertEqual(version, "1.0.13")
        self.assertEqual(marketplace["metadata"]["version"], version)
        self.assertEqual(marketplace["plugins"][0]["version"], version)
        readme = (ROOT / "README.md").read_text()
        changelog = (ROOT / "CHANGELOG.md").read_text()
        self.assertIn(f"version-{version}-blue.svg", readme)
        self.assertEqual(set(re.findall(r"version-(\d+\.\d+\.\d+)-blue\.svg", readme)), {version})
        self.assertIn("## Unreleased", changelog)
        latest_release = re.search(r"^## \[(\d+\.\d+\.\d+)\] - \d{4}-\d{2}-\d{2}$", changelog, re.MULTILINE)
        self.assertIsNotNone(latest_release)
        self.assertEqual(latest_release.group(1), version)

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

    def test_release_and_ci_gates_include_required_uv_smoke(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ark-check.yml").read_text()
        release = (ROOT / "RELEASE.md").read_text()
        smoke = (ROOT / "scripts" / "ark-smoke.py").read_text()

        for token in (
            "python -m pip install uv",
            "python scripts/ark-release-check.py --list",
            "uv run python scripts/ark-check.py",
            "uv run python scripts/ark-release-check.py --list",
            "uv run python scripts/ark-smoke.py --require-uv",
            "uv run python scripts/ark-skill-smoke.py",
            "uv run python scripts/ark-review-gate-smoke.py",
            "uv run python -m unittest discover -s tests",
            "claude plugin validate .",
            "Claude Code CLI not available; skipping plugin validate.",
            "python scripts/ark-skill-smoke.py",
            "python scripts/ark-review-gate-smoke.py",
        ):
            self.assertIn(token, workflow)

        for token in (
            "python scripts/ark-release-check.py",
            "python scripts/ark-release-check.py --list",
            "python scripts/ark-check.py --release",
            "python scripts/ark-smoke.py --require-uv",
            "python scripts/ark-skill-smoke.py",
            "python scripts/ark-review-gate-smoke.py",
            "uv run python scripts/ark-check.py --release",
            "uv run python scripts/ark-smoke.py --require-uv",
            "uv run python scripts/ark-skill-smoke.py",
            "uv run python scripts/ark-review-gate-smoke.py",
            "claude plugin validate .",
            "/plugin install ark@ark",
            "/plugin update ark@ark",
        ):
            self.assertIn(token, release)

        self.assertIn("--require-uv", smoke)
        self.assertIn("uv bare smoke was required", smoke)

    def test_skill_smoke_contract_assets_exist(self) -> None:
        skill_smoke = (ROOT / "scripts" / "ark-skill-smoke.py").read_text()

        for token in (
            "hello-ark-api",
            "GET /hello",
            "Hello, ARK!",
            "UV_CACHE_DIR",
            "UV_PYTHON_INSTALL_DIR",
            "uv run --no-project --python",
            "Failure summary:",
            "Failed command:",
            "Next steps:",
            "Temporary project cleaned.",
            "Temporary project kept for inspection:",
            "Ready for validation",
            "validation.md #验证记录 2026-06-03",
        ):
            self.assertIn(token, skill_smoke)

    def test_release_check_script_lists_release_gates(self) -> None:
        release_check = (ROOT / "scripts" / "ark-release-check.py").read_text()
        for token in (
            "python scripts/ark-check.py --release",
            "python scripts/ark-skill-smoke.py",
            "python scripts/ark-review-gate-smoke.py",
            "uv run python scripts/ark-check.py --release",
            "uv run python scripts/ark-skill-smoke.py",
            "uv run python scripts/ark-review-gate-smoke.py",
            "uv run python -m unittest discover -s tests",
            "claude plugin validate .",
            "--list",
            "--require-claude",
            "--skip-claude",
        ):
            self.assertIn(token, release_check)

        result = subprocess.run(
            [sys.executable, "scripts/ark-release-check.py", "--list"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for token in (
            "python scripts/ark-check.py --release",
            "python scripts/ark-skill-smoke.py",
            "python scripts/ark-review-gate-smoke.py",
            "uv run python scripts/ark-skill-smoke.py",
            "uv run python scripts/ark-review-gate-smoke.py",
            "claude plugin validate .",
        ):
            self.assertIn(token, result.stdout)

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
        self.assertIn("外部审查 evidence", validation_template)
        self.assertIn("外部 Verdict", validation_template)
        self.assertIn("Findings 状态", validation_template)
        self.assertIn("复检状态", validation_template)
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

    def test_external_review_gate_contract_assets_exist(self) -> None:
        gate_skill = (ROOT / "skills/ark-review-gate/SKILL.md").read_text()
        gate_rule = (ROOT / "rules/external-review-gate.md").read_text()
        implement_skill = (ROOT / "skills/ark-implement/SKILL.md").read_text()
        debug_skill = (ROOT / "skills/ark-debug/SKILL.md").read_text()
        validate_skill = (ROOT / "skills/ark-validate/SKILL.md").read_text()
        handoff_template = (ROOT / "templates/artifacts/handoff.template.md").read_text()
        memory_template = (ROOT / "templates/project/MEMORY.md.template").read_text()
        readme = (ROOT / "README.md").read_text()

        for token in (
            "高风险不过夜，低风险不单审",
            "immediate",
            "batch-candidate",
            "batch-ready",
            "blocked",
            "prepare",
            "import",
            "recheck",
            "必须修复",
            "可延期",
            "不处理",
            "External Review Gate",
            "不得修改源代码",
            "不得写入 `docs/ark/validation.md`",
            "不得把 task 标记为 Done",
            "不得把外部 review findings 直接改成 tasks",
            "validation.md：不写入",
            "tasks.md：不标记 Done",
        ):
            self.assertIn(token, gate_skill)

        for token in (
            "高风险不过夜",
            "低风险不单审",
            "小批量有上限",
            "复检不扩域",
            "review 不替代 validate",
            "外部审查 evidence",
        ):
            self.assertIn(token, gate_rule)

        self.assertIn("External Review Gate 轻量评估", implement_skill)
        self.assertIn("/ark:ark-review-gate prepare", implement_skill)
        self.assertIn("/ark:ark-review-gate import", debug_skill)
        self.assertIn("只修复必须修复项", debug_skill)
        self.assertIn("external review pending", validate_skill)
        self.assertIn("Done 还必须有外部审查 evidence", validate_skill)
        self.assertIn("## External Review Gate", handoff_template)
        self.assertIn("external-review-gate.md", memory_template)
        self.assertIn("23 个专责 Skill", readme)
        self.assertIn("/ark:ark-review-gate", readme)
        self.assertIn("ARK 内置 13 个规则文件", readme)

    def test_review_gate_smoke_contract_passes(self) -> None:
        review_gate_smoke = (ROOT / "scripts/ark-review-gate-smoke.py").read_text()
        good_fixture = (
            ROOT / "tests/fixtures/contracts/review-gate-smoke.good.md"
        ).read_text()
        bad_fixture = (
            ROOT / "tests/fixtures/contracts/review-gate-smoke.bad.md"
        ).read_text()

        for token in (
            "Review Gate Smoke Good Fixture",
            "review-gate-smoke.good.md",
            "review-gate-smoke.bad.md",
            "Gate 结论：immediate",
            "Gate 结论：batch-candidate",
            "Gate 结论：batch-ready",
            "外部审查状态：findings-imported",
            "外部审查状态：recheck-pending",
            "外部审查状态：passed",
            "validation.md：已更新",
            "tasks.md：已更新",
        ):
            self.assertIn(token, review_gate_smoke)

        self.assertIn("validation.md：不写入", good_fixture)
        self.assertIn("tasks.md：不标记 Done", good_fixture)
        self.assertIn("validation.md：已更新", bad_fixture)
        self.assertIn("tasks.md：已更新", bad_fixture)

        result = subprocess.run(
            [sys.executable, "scripts/ark-review-gate-smoke.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_snippet_contract_assets_exist(self) -> None:
        validation_snippet = (
            ROOT / "templates/snippets/validation-entry.snippet.md"
        ).read_text()
        decision_snippet = (
            ROOT / "templates/snippets/decision-record.snippet.md"
        ).read_text()
        decide_skill = (ROOT / "skills/ark-decide/SKILL.md").read_text()

        for token in (
            "验证覆盖范围",
            "覆盖任务",
            "覆盖原因",
            "未覆盖任务",
            "不覆盖原因",
            "外部审查 evidence",
            "外部 Verdict",
            "Findings 状态",
            "复检状态",
            "未做外部审查原因",
            "阶段推进路径",
        ):
            self.assertIn(token, validation_snippet)

        self.assertIn("- Title:", decision_snippet)
        self.assertIn("- Date:", decision_snippet)
        self.assertIn("不得保留空标题", decision_snippet)
        self.assertNotIn("## Decision: <标题>", decision_snippet)
        self.assertNotIn("- Date: YYYY-MM-DD", decision_snippet)

        for token in ("真实标题", "真实日期", "YYYY-MM-DD", "<标题>"):
            self.assertIn(token, decide_skill)

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
