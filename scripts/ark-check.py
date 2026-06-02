#!/usr/bin/env python3
"""Repository checks for ARK plugin assets and workflow contracts."""

from __future__ import annotations

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

    changelog = ROOT / "CHANGELOG.md"
    if not changelog.exists():
        fail(errors, "missing CHANGELOG.md for explicit versioned releases")
    elif f"## [{version}]" not in read(changelog):
        fail(errors, f"CHANGELOG.md missing release entry for {version}")


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
    for token in ("Ready for validation", "完成后可观察结果", "外部依据"):
        if token not in tasks:
            fail(errors, f"tasks.template.md missing {token}")
    if "## Last updated" in tasks:
        fail(errors, "tasks.template.md should use header last-updated only")

    spec = read(artifact_dir / "spec.template.md")
    if "核心命题与不变量" not in spec:
        fail(errors, "spec.template.md missing core proposition section")

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
        "templates/snippets/decision-record.snippet.md": ("方案 A", "方案 B"),
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
    next_skill = read(ROOT / "skills" / "ark-next" / "SKILL.md")
    claude_template = read(ROOT / "templates" / "project" / "CLAUDE.md.template")

    if "不得直接写入任何 `docs/ark/*`" not in solution:
        fail(errors, "ark-solution must forbid direct docs/ark writes")
    if "solution writer" not in protocol or "明确分配的扩展文档 write set" not in protocol:
        fail(errors, "sub-agent protocol missing solution writer write set rule")
    for token in ("只验证和记录，不修复", "不得修改任何源代码文件", "保真度 L0-L5"):
        if token not in validate:
            fail(errors, f"ark-validate missing validation boundary token: {token}")
    for token in ("保真度", "真实性锚点", "替身使用", "当前不可接受风险"):
        if token not in snippet:
            fail(errors, f"validation-entry.snippet.md missing token: {token}")
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


def check_release_and_ci_assets(errors: list[str]) -> None:
    workflow = ROOT / ".github" / "workflows" / "ark-check.yml"
    if not workflow.exists():
        fail(errors, "missing .github/workflows/ark-check.yml")
    else:
        text = read(workflow)
        for token in ("python scripts/ark-check.py", "python scripts/ark-smoke.py", "python -m unittest"):
            if token not in text:
                fail(errors, f"ark-check workflow missing command: {token}")

    if not (ROOT / "scripts" / "ark-smoke.py").exists():
        fail(errors, "missing scripts/ark-smoke.py")
    if not (ROOT / "tests").exists():
        fail(errors, "missing tests directory")
    if not (ROOT / "RELEASE.md").exists():
        fail(errors, "missing RELEASE.md")
    else:
        release = read(ROOT / "RELEASE.md")
        for token in (CANONICAL_UV_INIT, "git status --short", "[project.scripts]"):
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
            "fastchain-enhanced",
            "注释详细度分级",
            "不主动新增顶部模块级 docstring",
            "变量后置三引号",
            "句末中文终止标点",
        ],
        "skills/ark-validate/SKILL.md": [
            "Ready for validation → Done",
            "Checkpoint 建议",
        ],
        "skills/ark-review/SKILL.md": [
            "fastchain-enhanced",
            "注释详细度分级",
            "顶部模块级 docstring",
            "变量后置三引号",
            "句末中文终止标点",
            "尾随解释注释",
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


def main() -> int:
    errors: list[str] = []
    check_versions(errors)
    check_artifact_templates(errors)
    check_ruff_snippet(errors)
    check_skill_references(errors)
    check_skill_frontmatter(errors)
    check_init_contracts(errors)
    check_placeholder_policy(errors)
    check_subagent_and_validation_contracts(errors)
    check_stage_contracts(errors)
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
