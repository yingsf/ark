#!/usr/bin/env python3
"""Repository checks for ARK plugin assets and workflow contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
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
STAGE_TEMPLATES = {
    "stages": "stages.template.md",
    "stage-summary": "stage-summary.template.md",
}
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
README_VERSION_BADGE_RE = re.compile(r"version-(\d+\.\d+\.\d+)-blue\.svg")
CHANGELOG_VERSION_RE = re.compile(
    r"^## \[(?P<version>\d+\.\d+\.\d+)\] - (?P<date>\d{4}-\d{2}-\d{2})$",
    re.MULTILINE,
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def unreleased_body(changelog_text: str) -> str:
    match = re.search(r"^## Unreleased\s*$", changelog_text, re.MULTILINE)
    if not match:
        return ""
    next_release = re.search(r"^## \[\d+\.\d+\.\d+\]", changelog_text[match.end() :], re.MULTILINE)
    if not next_release:
        return changelog_text[match.end() :].strip()
    return changelog_text[match.end() : match.end() + next_release.start()].strip()


def check_changelog_contract(
    errors: list[str],
    changelog_text: str,
    version: str,
    release_mode: bool,
) -> None:
    if not changelog_text.startswith("# Changelog"):
        fail(errors, "CHANGELOG.md should start with # Changelog")
    if "## Unreleased" not in changelog_text:
        fail(errors, "CHANGELOG.md missing ## Unreleased section")

    matches = list(CHANGELOG_VERSION_RE.finditer(changelog_text))
    if not matches:
        fail(errors, "CHANGELOG.md missing versioned release entries")
        return

    versions = [match.group("version") for match in matches]
    duplicate_versions = sorted({item for item in versions if versions.count(item) > 1})
    if duplicate_versions:
        fail(errors, "CHANGELOG.md contains duplicate release entries: " + ", ".join(duplicate_versions))

    latest_version = versions[0]
    if latest_version != version:
        fail(
            errors,
            f"CHANGELOG.md latest release entry is {latest_version}, expected {version}",
        )
    if version not in versions:
        fail(errors, f"CHANGELOG.md missing release entry for {version}")

    if release_mode and unreleased_body(changelog_text):
        fail(
            errors,
            "CHANGELOG.md has Unreleased content; move it to the target version before release",
        )


def check_versions(errors: list[str], release_mode: bool = False) -> None:
    plugin = json.loads(read(ROOT / ".claude-plugin" / "plugin.json"))
    marketplace = json.loads(read(ROOT / ".claude-plugin" / "marketplace.json"))
    version = plugin.get("version")
    plugin_name = plugin.get("name")

    if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
        fail(errors, "plugin.json version must use semantic x.y.z format")

    if marketplace.get("metadata", {}).get("version") != version:
        fail(errors, "marketplace metadata version does not match plugin.json")

    matching_plugins = [
        item for item in marketplace.get("plugins", []) if item.get("name") == plugin_name
    ]
    if len(matching_plugins) != 1:
        fail(errors, "marketplace must contain exactly one plugin entry matching plugin.json name")
    for item in matching_plugins:
        if item.get("version") != version:
            fail(errors, "marketplace plugin version does not match plugin.json")

    readme = read(ROOT / "README.md")
    badge = f"version-{version}-blue.svg"
    if badge not in readme:
        fail(errors, f"README version badge does not contain {badge}")
    readme_badges = sorted(set(README_VERSION_BADGE_RE.findall(readme)))
    stale_badges = [item for item in readme_badges if item != version]
    if stale_badges:
        fail(errors, "README contains stale version badge(s): " + ", ".join(stale_badges))

    changelog = ROOT / "CHANGELOG.md"
    if not changelog.exists():
        fail(errors, "missing CHANGELOG.md for explicit versioned releases")
    else:
        check_changelog_contract(errors, read(changelog), version, release_mode)


def check_artifact_templates(errors: list[str]) -> None:
    artifact_dir = ROOT / "templates" / "artifacts"

    for artifact, filename in ARTIFACTS.items():
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
    for token in (
        "Ready for validation",
        "完成后可观察结果",
        "外部依据",
        "功能/技术闭环",
        "实施要点",
        "建议验证方式",
        "可与哪些任务合并验证",
        "3-8 个任务",
    ):
        if token not in tasks:
            fail(errors, f"tasks.template.md missing {token}")
    if "## Last updated" in tasks:
        fail(errors, "tasks.template.md should use header last-updated only")

    validation = read(artifact_dir / "validation.template.md")
    for token in ("## 验证覆盖范围", "覆盖任务", "覆盖原因", "未覆盖任务"):
        if token not in validation:
            fail(errors, f"validation.template.md missing {token}")
    if "阶段表" in validation:
        fail(errors, "validation.template.md should reference 阶段推进路径, not 阶段表")

    spec = read(artifact_dir / "spec.template.md")
    if "核心命题与不变量" not in spec:
        fail(errors, "spec.template.md missing core proposition section")
    for token in ("用户可观察能力", "不得写成文件/函数级实现步骤"):
        if token not in spec:
            fail(errors, f"spec.template.md missing {token}")

    design = read(artifact_dir / "design.template.md")
    for token in (
        "## 技术闭环建议",
        "最小可运行闭环",
        "最小契约验证",
        "不建议拆分为 task 的低层实现点",
    ):
        if token not in design:
            fail(errors, f"design.template.md missing {token}")

    plan = read(artifact_dir / "plan.template.md")
    for token in (
        "## 阶段推进路径",
        "交付单元 / 技术闭环",
        "建议 task 边界",
        "不建议拆分为",
    ):
        if token not in plan:
            fail(errors, f"plan.template.md missing {token}")

    forbidden_placeholders = {
        "spec.template.md": ("标准 1", "标准 2", "问题 1", "问题 2"),
        "design.template.md": ("docs/solution/example.md", "方案 A", "方案 B"),
        "plan.template.md": ("阶段 1 |", "阶段 2 |", "风险 1", "验证方式 1"),
        "decisions.template.md": ("方案 A", "方案 B", "方案 C", "<标题>"),
        "validation.template.md": ("验证项 1", "未覆盖项 1", "建议项 1", "无法验证项 1"),
        "handoff.template.md": ("项目 1", "下一步动作 1", "`/ark:ark-implement`"),
    }
    for filename, tokens in forbidden_placeholders.items():
        text = read(artifact_dir / filename)
        for token in tokens:
            if token in text:
                fail(errors, f"{filename} contains high-risk placeholder: {token}")


def check_ruff_snippet(errors: list[str]) -> None:
    snippet = read(ROOT / "templates" / "project" / "pyproject-ruff.snippet.toml")
    for rule in ("RUF001", "RUF002", "RUF003"):
        if rule not in snippet:
            fail(errors, f"Ruff snippet missing {rule} ignore")
    if 'known-first-party = ["<package_name>"]' not in snippet:
        fail(errors, "Ruff snippet should use <package_name> for first-party package")
    if 'known-first-party = ["<project_name>"]' in snippet:
        fail(errors, "Ruff snippet should not use <project_name> for first-party package")


def check_skill_references(errors: list[str]) -> None:
    pattern = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)")
    for base in ("skills", "rules", "templates"):
        paths = (ROOT / base).rglob("*.md")
        for path in paths:
            text = read(path)
            for rel in pattern.findall(text):
                target = ROOT / rel
                if not target.exists():
                    fail(
                        errors,
                        f"{path.relative_to(ROOT)} references missing path: {rel}",
                    )


def check_skill_frontmatter(errors: list[str]) -> None:
    for path in (ROOT / "skills").rglob("SKILL.md"):
        text = read(path)
        rel = path.relative_to(ROOT)
        expected_name = path.parent.name
        required = (f"name: {expected_name}", "description:", "version:")
        for token in required:
            if token not in text:
                fail(errors, f"{rel} missing frontmatter token: {token}")


def check_init_contracts(errors: list[str]) -> None:
    init_skill = read(ROOT / "skills" / "ark-init" / "SKILL.md")
    init_reference = read(
        ROOT / "skills" / "ark-init" / "references" / "project-bootstrap-guidelines.md"
    )
    fallback = read(
        ROOT / "skills" / "ark-init" / "references" / "fallback-templates.md"
    )

    for rel, text in (
        ("skills/ark-init/SKILL.md", init_skill),
        ("skills/ark-init/references/project-bootstrap-guidelines.md", init_reference),
    ):
        if CANONICAL_UV_INIT not in text:
            fail(errors, f"{rel} missing canonical uv init command")
        old_uv_tokens = (
            "uv init <project_name>",
            "uv init --name <project_name>",
            "uv init --name <distribution_name> --python",
            "uv init --no-workspace\n",
        )
        for token in old_uv_tokens:
            if token in text:
                fail(errors, f"{rel} contains non-canonical uv init command: {token}")
        for token in (
            "<distribution_name>",
            "<package_name>",
            "[project.scripts]",
            "uv sample function",
            'packages = ["src/<package_name>"]',
        ):
            if token not in text:
                fail(errors, f"{rel} missing bare-init contract token: {token}")
        if "`uv init --bare`" not in text and "uv init --bare --name" not in text:
            fail(errors, f"{rel} missing explicit uv --bare requirement")
        if 'packages = ["src/<project_name>"]' in text:
            fail(errors, f"{rel} contains non-canonical uv init command")
        if "hatchling.backends" in text and "不得写成 `hatchling.backends`" not in text:
            fail(errors, f"{rel} contains unsafe hatchling.backends reference")

    forbidden_empty_fallback = ("创建空文件", "创建为空文件", "纯空文件。若模板文件存在")
    for token in forbidden_empty_fallback:
        if token in init_reference or token in fallback:
            fail(errors, f"init fallback contract still contains stale token: {token}")

    for artifact in ARTIFACTS:
        header = f"<!-- ark-artifact: {artifact} -->"
        if header not in fallback:
            fail(errors, f"fallback-templates.md missing fallback header for {artifact}")
    for token in ("<!-- schema-version: 1.1 -->", "<!-- last-updated: YYYY-MM-DD -->"):
        if fallback.count(token) < len(ARTIFACTS):
            fail(errors, f"fallback-templates.md should contain {token} for each artifact")

    for token in (
        'name = "<distribution_name>"',
        'packages = ["src/<package_name>"]',
        'known-first-party = ["<package_name>"]',
        "包名为 `<package_name>`",
        "功能/技术闭环",
        "实施要点",
        "可与哪些任务合并验证",
        "验证覆盖范围",
        "覆盖原因",
        "技术闭环建议",
        "建议 task 边界",
        "不建议拆分为",
    ):
        if token not in fallback:
            fail(errors, f"fallback-templates.md missing naming token: {token}")
    for token in (
        'name = "<project_name>"',
        'packages = ["src/<project_name>"]',
        'known-first-party = ["<project_name>"]',
        "包名为 `<project_name>`",
    ):
        if token in fallback:
            fail(errors, f"fallback-templates.md contains ambiguous naming token: {token}")


def check_placeholder_policy(errors: list[str]) -> None:
    policy = ROOT / "rules" / "artifact-placeholder-policy.md"
    if not policy.exists():
        fail(errors, "missing rules/artifact-placeholder-policy.md")
        return

    required_refs = (
        "skills/ark-analyze/SKILL.md",
        "skills/ark-spec/SKILL.md",
        "skills/ark-design/SKILL.md",
        "skills/ark-sync/SKILL.md",
        "skills/ark-next/SKILL.md",
        "skills/ark-stage/SKILL.md",
        "templates/project/MEMORY.md.template",
        "skills/ark-init/references/fallback-templates.md",
    )
    for rel in required_refs:
        text = read(ROOT / rel)
        if "artifact-placeholder-policy.md" not in text:
            fail(errors, f"{rel} missing artifact-placeholder-policy.md reference")

    snippet_forbidden = {
        "templates/snippets/handoff-entry.snippet.md": (
            "项目 1",
            "下一步动作 1",
        ),
        "templates/snippets/validation-entry.snippet.md": (
            "验证项 1",
            "未覆盖项 1",
            "建议项 1",
            "无法验证项 1",
        ),
        "templates/snippets/decision-record.snippet.md": (
            "方案 A",
            "方案 B",
            "Date: YYYY-MM-DD",
        ),
    }
    for rel, tokens in snippet_forbidden.items():
        text = read(ROOT / rel)
        for token in tokens:
            if token in text:
                fail(errors, f"{rel} contains high-risk placeholder: {token}")


def check_subagent_and_validation_contracts(errors: list[str]) -> None:
    solution = read(ROOT / "skills" / "ark-solution" / "SKILL.md")
    protocol = read(ROOT / "rules" / "sub-agent-protocol.md")
    validate = read(ROOT / "skills" / "ark-validate" / "SKILL.md")
    snippet = read(ROOT / "templates" / "snippets" / "validation-entry.snippet.md")
    decision_snippet = read(ROOT / "templates" / "snippets" / "decision-record.snippet.md")
    next_skill = read(ROOT / "skills" / "ark-next" / "SKILL.md")
    claude_template = read(ROOT / "templates" / "project" / "CLAUDE.md.template")

    if "不得直接写入任何 `docs/ark/*`" not in solution:
        fail(errors, "ark-solution must forbid direct docs/ark writes")
    if "solution writer" not in protocol or "明确分配的扩展文档 write set" not in protocol:
        fail(errors, "sub-agent protocol missing solution writer write set rule")
    for token in ("只验证和记录，不修复", "不得修改任何源代码文件", "保真度 L0-L5"):
        if token not in validate:
            fail(errors, f"ark-validate missing validation boundary token: {token}")
    for token in (
        "保真度",
        "真实性锚点",
        "替身使用",
        "当前不可接受风险",
        "验证覆盖范围",
        "覆盖任务",
        "覆盖原因",
        "未覆盖任务",
        "不覆盖原因",
        "阶段推进路径",
    ):
        if token not in snippet:
            fail(errors, f"validation-entry.snippet.md missing token: {token}")
    for token in ("Title:", "Date:", "不得保留空标题", "YYYY-MM-DD", "<标题>"):
        if token not in decision_snippet:
            fail(errors, f"decision-record.snippet.md missing token: {token}")
    if "## Decision: <标题>" in decision_snippet or "- Date: YYYY-MM-DD" in decision_snippet:
        fail(errors, "decision-record.snippet.md contains high-risk inline placeholder")
    if "只读取 docs，不更新任何 Artifact" not in next_skill:
        fail(errors, "ark-next should be read-only and recommend sync/handoff for writes")
    if "按对应 ARK Skill 的可写范围更新 Artifact" not in claude_template:
        fail(errors, "CLAUDE.md.template should scope Artifact updates by Skill write range")


def check_stage_contracts(errors: list[str]) -> None:
    skill_path = ROOT / "skills" / "ark-stage" / "SKILL.md"
    if not skill_path.exists():
        fail(errors, "missing skills/ark-stage/SKILL.md")
        return

    stage_skill = read(skill_path)
    required_skill_tokens = (
        "stage-status",
        "stage-close",
        "stage-open",
        "stage-transition",
        "preview",
        "用户确认",
        "closed-with-risk",
        "Carryover Gates",
        "docs/ark/archive/<stage-id>/",
        "docs/ark/stages.md",
        "不得静默写成 `closed`",
        "禁止写",
        "源代码",
        "真实数据内容",
        "项目级长期记忆",
        "当前仍有效决策索引",
        "不得生成空的 `decisions.md`",
        "不确定时默认保留",
        "`stage-close` 只归档",
        "superseded",
        "${CLAUDE_PLUGIN_ROOT}/templates/stage/stage-summary.template.md",
        "${CLAUDE_PLUGIN_ROOT}/templates/stage/stages.template.md",
    )
    for token in required_skill_tokens:
        if token not in stage_skill:
            fail(errors, f"ark-stage missing stage contract token: {token}")

    stage_dir = ROOT / "templates" / "stage"
    for name, filename in STAGE_TEMPLATES.items():
        path = stage_dir / filename
        if not path.exists():
            fail(errors, f"missing stage template: templates/stage/{filename}")
            continue
        text = read(path)
        if not text.strip():
            fail(errors, f"templates/stage/{filename} is empty")
        if name == "stages":
            for token in (
                "<!-- ark-artifact: stages -->",
                "<!-- schema-version: 1.0 -->",
                "<!-- last-updated: YYYY-MM-DD -->",
                "## Current Stage",
                "## Stage History",
                "## Carryover Gates",
                "## Long-Lived Inheritance",
            ):
                if token not in text:
                    fail(errors, f"stages.template.md missing token: {token}")
        if name == "stage-summary":
            for token in (
                "<!-- ark-stage-summary: <stage-id> -->",
                "<!-- schema-version: 1.0 -->",
                "<!-- generated-at: YYYY-MM-DD -->",
                "## 1. 阶段结论",
                "## 4. 验证摘要",
                "## 5. 可继承结论",
                "## 6. 不应继承的内容",
                "继续保留到当前 `decisions.md`",
                "标记为 `superseded` / 已替代",
                "不确定但默认保留",
            ):
                if token not in text:
                    fail(errors, f"stage-summary.template.md missing token: {token}")

    readme = read(ROOT / "README.md")
    for token in (
        "22 个专责 Skill",
        "/ark:ark-stage",
        "closed-with-risk",
        "Carryover Gates",
        "项目级长期记忆",
        "superseded",
    ):
        if token not in readme:
            fail(errors, f"README.md missing ark-stage token: {token}")

    ark_rule = read(ROOT / "rules" / "ark.md")
    if "ark-stage" not in ark_rule or "阶段收口" not in ark_rule:
        fail(errors, "rules/ark.md missing ark-stage routing")


def check_review_contracts(errors: list[str]) -> None:
    skill_rel = "skills/ark-review/SKILL.md"
    contract_rel = "skills/ark-review/references/contract-driven-python-review.md"
    craft_rel = "skills/ark-review/references/craftsmanship-review.md"
    recheck_rel = "skills/ark-review/references/recheck-guidelines.md"

    review_skill = read(ROOT / skill_rel)
    for rel in (contract_rel, craft_rel, recheck_rel):
        if f"${{CLAUDE_PLUGIN_ROOT}}/{rel}" not in review_skill:
            fail(errors, f"{skill_rel} missing review reference: {rel}")

    for token in (
        "深度契约驱动",
        "任务契约",
        "测试通过但业务语义不对",
        "fail-closed",
        "Craftsmanship 不等于 Finding",
        "Review 只观察、判断和建议",
        "## Findings",
        "## Craftsmanship",
        "## Verification",
        "## Open Questions",
        "## ARK Follow-up",
        "## Verdict",
        "Location: `path:line`",
    ):
        if token not in review_skill:
            fail(errors, f"{skill_rel} missing deep review token: {token}")

    contract = read(ROOT / contract_rel)
    for token in (
        "契约识别",
        "跨层口径一致性",
        "fail-closed",
        "敏感信息",
        "测试通过但业务语义不对",
        "deep copy",
        "排序、去重、聚合专项",
        "类型与运行时一致性",
    ):
        if token not in contract:
            fail(errors, f"{contract_rel} missing contract-review token: {token}")

    craft = read(ROOT / craft_rel)
    for token in (
        "Craftsmanship 不等于 Finding",
        "Upgrade",
        "Polish",
        "Keep",
        "Do now",
        "API 设计",
        "数据边界",
        "错误语义",
        "测试质量",
    ):
        if token not in craft:
            fail(errors, f"{craft_rel} missing craftsmanship token: {token}")

    recheck = read(ROOT / recheck_rel)
    for token in (
        "复审",
        "上一轮 Findings",
        "修复前会失败",
        "修复后会通过",
        "破坏原有主路径",
        "新的 Finding",
    ):
        if token not in recheck:
            fail(errors, f"{recheck_rel} missing recheck token: {token}")


def check_execution_efficiency_contracts(errors: list[str]) -> None:
    checks = {
        "skills/ark-tasks/SKILL.md": (
            "功能交付单元",
            "可验证技术闭环",
            "实施要点",
            "默认只展开当前可执行窗口的 3-8 个任务",
            "低层步骤应写入任务的「实施要点」",
            "多个 Done 任务可以引用同一条记录",
        ),
        "skills/ark-implement/SKILL.md": (
            "显式功能 Batch 例外",
            "功能结果",
            "本次新增 / 改变的能力",
            "用户或调用方如何触发",
            "用户验收方式",
            "当前完成状态",
            "任务状态建议",
            "统一验证计划",
            "默认输出必须包含功能结果",
            "条件输出",
            "仅在已启用、失败、降级或影响可信度时输出",
        ),
        "skills/ark-implement/references/comment-docstring-guidelines.md": (
            "fastchain-enhanced",
            "L0 无需补充",
            "L2 fastchain-enhanced",
            "不主动新增顶部模块级 docstring",
            "变量后置三引号",
            "句末中文终止标点",
            "解释性尾随注释",
        ),
        "skills/ark-implement/references/batch-subagent-guidelines.md": (
            "显式功能 Batch",
            "统一验证计划",
            "batch write set",
            "write set",
            "Checkpoint 建议",
            "Sub-agent 状态",
        ),
        "skills/ark-validate/SKILL.md": (
            "验证覆盖范围",
            "覆盖任务",
            "覆盖原因",
            "同一功能闭环",
            "不得用一条宽泛验证记录覆盖无关任务",
        ),
        "rules/task-sizing-rules.md": (
            "任务粒度原则",
            "功能交付单元",
            "可验证技术闭环",
            "验证可以聚合",
            "spec.md",
            "design.md",
            "plan.md",
            "建议 task 边界",
        ),
        "rules/task-sizing-summary.md": (
            "Task 粒度",
            "当前执行窗口建议 3-8 个 task",
            "明确覆盖范围",
            "design",
            "plan",
        ),
        "rules/artifact-update-policy.md": (
            "验证可聚合但不能泛化",
            "功能交付单元或可验证技术闭环",
            "覆盖任务、覆盖原因和未覆盖任务",
            "技术闭环建议",
            "建议 task 边界",
        ),
        "rules/artifact-roles.md": (
            "任务粒度服务闭环",
            "验证可聚合",
            "罗列文件/函数级实现步骤",
            "上游不制造碎片",
        ),
        "README.md": (
            "从 1.0.8 起",
            "从 1.0.9 起",
            "从 1.0.10 起",
            "从 1.0.11 起",
            "从 1.0.12 起",
            "功能交付单元或可验证技术闭环",
            "功能结果",
            "用户验收方式",
            "同闭环任务可以作为明确 batch",
        ),
    }

    for rel, tokens in checks.items():
        text = read(ROOT / rel)
        for token in tokens:
            if token not in text:
                fail(errors, f"{rel} missing execution efficiency token: {token}")

    forbidden = {
        "skills/ark-implement/SKILL.md": ("功能视角",),
        "templates/artifacts/validation.template.md": ("阶段表",),
        "templates/artifacts/plan.template.md": ("阶段表",),
        "skills/ark-plan/SKILL.md": ("阶段表",),
        "rules/task-sizing-rules.md": ("阶段表",),
    }
    for rel, tokens in forbidden.items():
        text = read(ROOT / rel)
        for token in tokens:
            if token in text:
                fail(errors, f"{rel} contains stale contract token: {token}")


def plan_granularity_errors(text: str) -> list[str]:
    errors: list[str] = []
    for token in (
        "阶段推进路径",
        "交付单元 / 技术闭环",
        "建议 task 边界",
        "不建议拆分为",
    ):
        if token not in text:
            errors.append(f"missing {token}")
    if "阶段表" in text:
        errors.append("uses stale 阶段表")
    for pattern in (
        r"创建\s+\S+\.py",
        r"实现\s+\S+\s*函数",
        r"新增\s+\S+\s*配置项",
    ):
        if re.search(pattern, text):
            errors.append(f"contains file/function-level split: {pattern}")
    return errors


def implement_report_errors(text: str) -> list[str]:
    errors: list[str] = []
    for token in (
        "### 1. 功能结果",
        "当前完成状态",
        "任务状态建议",
        "用户验收方式",
        "### 3. 验证状态",
        "### 4. 风险与回写",
    ):
        if token not in text:
            errors.append(f"missing {token}")
    for token in ("功能视角", "### Sub-agent 状态", "模块级 docstring / 变量后置三引号检查"):
        if token in text:
            errors.append(f"contains default-report noise or stale token: {token}")
    return errors


def validation_coverage_errors(text: str) -> list[str]:
    errors: list[str] = []
    for token in ("验证覆盖范围", "覆盖任务", "覆盖原因", "未覆盖任务", "不覆盖原因"):
        if token not in text:
            errors.append(f"missing {token}")
    if "全部通过" in text and "覆盖任务" not in text:
        errors.append("uses broad validation without coverage mapping")
    return errors


def check_contract_fixtures(errors: list[str]) -> None:
    fixture_dir = ROOT / "tests" / "fixtures" / "contracts"
    checks = {
        "plan-granularity": plan_granularity_errors,
        "implement-report": implement_report_errors,
        "validation-coverage": validation_coverage_errors,
    }

    for name, checker in checks.items():
        good = fixture_dir / f"{name}.good.md"
        bad = fixture_dir / f"{name}.bad.md"
        if not good.exists():
            fail(errors, f"missing good contract fixture: {good.relative_to(ROOT)}")
            continue
        if not bad.exists():
            fail(errors, f"missing bad contract fixture: {bad.relative_to(ROOT)}")
            continue

        good_errors = checker(read(good))
        if good_errors:
            fail(errors, f"{good.relative_to(ROOT)} should pass contract check: {good_errors}")

        bad_errors = checker(read(bad))
        if not bad_errors:
            fail(errors, f"{bad.relative_to(ROOT)} should fail contract check")


def check_release_and_ci_assets(errors: list[str]) -> None:
    workflow = ROOT / ".github" / "workflows" / "ark-check.yml"
    if not workflow.exists():
        fail(errors, "missing .github/workflows/ark-check.yml")
    else:
        text = read(workflow)
        for token in (
            "python scripts/ark-check.py",
            "python scripts/ark-release-check.py --list",
            "python scripts/ark-smoke.py",
            "python scripts/ark-skill-smoke.py",
            "python -m unittest",
            "python -m pip install uv",
            "uv run python scripts/ark-check.py",
            "uv run python scripts/ark-release-check.py --list",
            "uv run python scripts/ark-smoke.py --require-uv",
            "uv run python scripts/ark-skill-smoke.py",
            "uv run python -m unittest discover -s tests",
            "claude plugin validate .",
            "Claude Code CLI not available; skipping plugin validate.",
        ):
            if token not in text:
                fail(errors, f"ark-check workflow missing command: {token}")

    smoke = ROOT / "scripts" / "ark-smoke.py"
    if not smoke.exists():
        fail(errors, "missing scripts/ark-smoke.py")
    else:
        smoke_text = read(smoke)
        for token in ("--require-uv", "uv bare smoke was required"):
            if token not in smoke_text:
                fail(errors, f"scripts/ark-smoke.py missing required uv smoke token: {token}")
    release_check = ROOT / "scripts" / "ark-release-check.py"
    if not release_check.exists():
        fail(errors, "missing scripts/ark-release-check.py")
    else:
        release_check_text = read(release_check)
        for token in (
            "python scripts/ark-check.py --release",
            "python scripts/ark-skill-smoke.py",
            "uv run python scripts/ark-check.py --release",
            "uv run python scripts/ark-skill-smoke.py",
            "uv run python -m unittest discover -s tests",
            "claude plugin validate .",
            "--list",
            "--require-claude",
            "--skip-claude",
        ):
            if token not in release_check_text:
                fail(errors, f"scripts/ark-release-check.py missing token: {token}")
    if not (ROOT / "tests").exists():
        fail(errors, "missing tests directory")
    skill_smoke = ROOT / "scripts" / "ark-skill-smoke.py"
    if not skill_smoke.exists():
        fail(errors, "missing scripts/ark-skill-smoke.py")
    else:
        skill_smoke_text = read(skill_smoke)
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
        ):
            if token not in skill_smoke_text:
                fail(errors, f"scripts/ark-skill-smoke.py missing token: {token}")
    if not (ROOT / "RELEASE.md").exists():
        fail(errors, "missing RELEASE.md")
    else:
        release = read(ROOT / "RELEASE.md")
        for token in (
            CANONICAL_UV_INIT,
            "git status --short",
            "[project.scripts]",
            "python scripts/ark-release-check.py",
            "python scripts/ark-release-check.py --list",
            "python scripts/ark-check.py --release",
            "python scripts/ark-smoke.py --require-uv",
            "python scripts/ark-skill-smoke.py",
            "uv run python scripts/ark-check.py --release",
            "uv run python scripts/ark-smoke.py --require-uv",
            "uv run python scripts/ark-skill-smoke.py",
            "claude plugin validate .",
            "/plugin install ark@ark",
            "/plugin update ark@ark",
        ):
            if token not in release:
                fail(errors, f"RELEASE.md missing release gate token: {token}")


def check_no_local_environment_binding(errors: list[str]) -> None:
    forbidden = ("rt" + "k", "RT" + "K.md", "/root/.codex/")
    scan_roots = (
        ROOT / "README.md",
        ROOT / "CHANGELOG.md",
        ROOT / "RELEASE.md",
        ROOT / ".claude-plugin",
        ROOT / ".github",
        ROOT / "rules",
        ROOT / "skills",
        ROOT / "templates",
        ROOT / "scripts",
        ROOT / "tests",
    )
    suffixes = {".md", ".json", ".toml", ".yml", ".yaml", ".py"}
    for root in scan_roots:
        if not root.exists():
            continue
        paths = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]
        for path in paths:
            if path == Path(__file__).resolve():
                continue
            if path.suffix not in suffixes:
                continue
            text = read(path)
            for token in forbidden:
                if token in text:
                    fail(
                        errors,
                        f"{path.relative_to(ROOT)} contains local environment binding: {token}",
                    )


def check_workflow_tokens(errors: list[str]) -> None:
    required = {
        "skills/ark-implement/SKILL.md": [
            "前序结论吸收",
            "Ready for validation",
            "Checkpoint 建议",
            "本轮唯一执行目标",
            "不得连续执行多个 Todo",
            "完成当前目标后停止",
            "功能结果",
            "用户验收方式",
        ],
        "skills/ark-implement/references/comment-docstring-guidelines.md": [
            "fastchain-enhanced",
            "L0 无需补充",
            "L2 fastchain-enhanced",
            "不主动新增顶部模块级 docstring",
            "变量后置三引号",
            "句末中文终止标点",
            "解释性尾随注释",
        ],
        "skills/ark-implement/references/batch-subagent-guidelines.md": [
            "显式功能 Batch",
            "统一验证计划",
            "batch write set",
            "write set",
            "Checkpoint 建议",
            "Sub-agent 状态",
        ],
        "skills/ark-validate/SKILL.md": [
            "Ready for validation → Done",
            "Checkpoint 建议",
        ],
        "skills/ark-review/SKILL.md": [
            "深度契约驱动",
            "任务契约",
            "测试通过但业务语义不对",
            "fail-closed",
            "Craftsmanship 不等于 Finding",
            "ARK Follow-up",
            "Verdict",
        ],
        "skills/ark-review/references/contract-driven-python-review.md": [
            "契约识别",
            "跨层口径一致性",
            "fail-closed",
            "敏感信息",
            "测试通过但业务语义不对",
            "deep copy",
        ],
        "skills/ark-review/references/craftsmanship-review.md": [
            "Craftsmanship 不等于 Finding",
            "Upgrade",
            "Polish",
            "Keep",
            "Do now",
        ],
        "skills/ark-review/references/recheck-guidelines.md": [
            "复审",
            "上一轮 Findings",
            "修复前会失败",
            "修复后会通过",
            "破坏原有主路径",
        ],
        "skills/ark-sync/SKILL.md": [
            "变更传播判断",
            "核心命题与不变量",
            "同一个 task ID 跨状态重复出现",
            "tasks 依赖顺序",
        ],
        "skills/ark-next/SKILL.md": [
            "当前最可信",
            "用户需提供的信息",
            "第一个可执行 Todo",
            "本轮唯一执行目标",
            "Carryover Gates",
        ],
        "skills/ark-handoff/SKILL.md": [
            "下一次必须继承的结论",
        ],
        "skills/ark-stage/SKILL.md": [
            "stage-status",
            "stage-close",
            "stage-open",
            "stage-transition",
            "closed-with-risk",
            "Carryover Gates",
            "docs/ark/archive/<stage-id>/",
            "stage-summary.md",
            "stages.md",
            "preview",
            "用户确认",
        ],
        "skills/ark-init/SKILL.md": [
            CANONICAL_UV_INIT,
            'build-backend = "hatchling.build"',
            "不得写成 `hatchling.backends`",
            "Mode A 不得静默使用 `unknown`",
            "不得默认建议 `/ark:ark-analyze`",
            "find . -maxdepth 1 -name 'requirements*.txt' -print",
            "检测命令失败不得继续当作",
            "每个质量工具配置写入后必须复查文件存在性",
            "必须使用 Claude Code 的交互式提问机制",
            "不得只在普通回复中输出",
            "模式选择不得通过普通文本问题完成",
            "不得生成纯空文件",
            "覆盖（高风险，必须二次确认）",
            "不得直接执行 `uv add --dev`",
            "本地辅助已创建",
            ".claude/settings.local.json",
            "质量工具配置 | 已创建 / 失败（原因）/ 待手动处理",
        ],
        "skills/ark-init/references/project-bootstrap-guidelines.md": [
            CANONICAL_UV_INIT,
            'build-backend = "hatchling.build"',
            "不得写成 `hatchling.backends`",
            "Mode A 不得静默使用 `unknown`",
            "Mode A 输出下一步规则",
            "find . -maxdepth 1 -name 'requirements*.txt' -print",
            "每个质量工具配置写入后必须复查文件存在性",
            "必须使用 Claude Code 的交互式提问机制",
            "不得只输出\"请选择初始化模式\"",
            "不得生成纯空文件",
            "覆盖（高风险，必须二次确认）",
            "不得直接执行 `uv add --dev`",
            "用户确认后可创建",
        ],
        "rules/python-backend-conventions.md": [
            "fastchain-enhanced",
            "L0 无需补充",
            "L2 fastchain-enhanced",
            "模块级 docstring 策略",
            "变量后置三引号",
            "中文标点规则",
            "解释性尾随注释",
        ],
        "rules/artifact-update-policy.md": [
            "本轮唯一执行目标",
            "不得连续执行多个 Todo",
            "同一个 task ID 不得跨状态重复出现",
            "Carryover Gates",
        ],
        "templates/project/CLAUDE.md.template": [
            "注释详细度：fastchain-enhanced",
            "不主动新增顶部模块级 docstring",
            "赋值语句后的三引号字符串",
            "句末中文终止标点",
            "解释性尾随注释",
        ],
        "skills/ark-init/references/fallback-templates.md": [
            "注释详细度：fastchain-enhanced",
            "不主动新增顶部模块级 docstring",
            "赋值语句后的三引号字符串",
            "句末中文终止标点",
            "解释性尾随注释",
            "artifact-placeholder-policy.md",
        ],
        "rules/artifact-placeholder-policy.md": [
            "非实质性内容",
            "实质性内容判定",
            "docs/solution/example.md",
            "ark-stage",
        ],
    }

    for rel, tokens in required.items():
        text = read(ROOT / rel)
        for token in tokens:
            if token not in text:
                fail(errors, f"{rel} missing workflow token: {token}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate ARK repository assets and release contracts."
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="enable strict release checks, including empty Unreleased changelog content",
    )
    args = parser.parse_args(argv)

    errors: list[str] = []
    check_versions(errors, release_mode=args.release)
    check_artifact_templates(errors)
    check_ruff_snippet(errors)
    check_skill_references(errors)
    check_skill_frontmatter(errors)
    check_init_contracts(errors)
    check_placeholder_policy(errors)
    check_subagent_and_validation_contracts(errors)
    check_stage_contracts(errors)
    check_review_contracts(errors)
    check_execution_efficiency_contracts(errors)
    check_contract_fixtures(errors)
    check_release_and_ci_assets(errors)
    check_no_local_environment_binding(errors)
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
