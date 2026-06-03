#!/usr/bin/env python3
"""Smoke checks for ARK external review gate state contracts."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GOOD_FIXTURE = ROOT / "tests" / "fixtures" / "contracts" / "review-gate-smoke.good.md"
BAD_FIXTURE = ROOT / "tests" / "fixtures" / "contracts" / "review-gate-smoke.bad.md"

REQUIRED_GOOD_TOKENS = (
    "Review Gate Smoke Good Fixture",
    "High-risk immediate",
    "Low-risk batch candidate",
    "Batch ready",
    "Findings imported",
    "Recheck pending",
    "Gate passed",
    "Gate 结论：immediate",
    "Gate 结论：batch-candidate",
    "Gate 结论：batch-ready",
    "外部审查状态：pending",
    "外部审查状态：package-prepared",
    "外部审查状态：findings-imported",
    "外部审查状态：recheck-pending",
    "外部审查状态：passed",
    "Findings 分类：必须修复 / 可延期 / 不处理",
    "下一步：/ark:ark-review-gate prepare",
    "下一步：/ark:ark-debug",
    "下一步：/ark:ark-review-gate recheck",
    "下一步：/ark:ark-validate",
    "validation.md：不写入",
    "tasks.md：不标记 Done",
)

FORBIDDEN_BOUNDARY_VIOLATIONS = (
    "validation.md：已更新",
    "tasks.md：已更新",
    "任务已 Done",
    "已修改源码",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def review_gate_trace_errors(text: str) -> list[str]:
    errors: list[str] = []
    for token in REQUIRED_GOOD_TOKENS:
        if token not in text:
            fail(errors, f"missing review gate trace token: {token}")
    for token in FORBIDDEN_BOUNDARY_VIOLATIONS:
        if token in text:
            fail(errors, f"contains review gate boundary violation: {token}")
    return errors


def smoke_contract_assets(errors: list[str]) -> None:
    skill = read(ROOT / "skills" / "ark-review-gate" / "SKILL.md")
    rule = read(ROOT / "rules" / "external-review-gate.md")
    handoff = read(ROOT / "templates" / "artifacts" / "handoff.template.md")

    for token in (
        "不得修改源代码",
        "不得写入 `docs/ark/validation.md`",
        "不得把 task 标记为 Done",
        "不得把外部 review findings 直接改成 tasks",
        "validation.md：不写入",
        "tasks.md：不标记 Done",
        "immediate",
        "batch-candidate",
        "batch-ready",
        "blocked",
        "prepare",
        "import",
        "recheck",
    ):
        if token not in skill:
            fail(errors, f"ark-review-gate skill missing token: {token}")

    for token in (
        "高风险不过夜",
        "低风险不单审",
        "小批量有上限",
        "复检不扩域",
        "review 不替代 validate",
        "外部审查 evidence",
    ):
        if token not in rule:
            fail(errors, f"external review gate rule missing token: {token}")

    for token in ("## External Review Gate", "外部审查状态", "Gate 结论"):
        if token not in handoff:
            fail(errors, f"handoff template missing token: {token}")


def smoke_fixtures(errors: list[str]) -> None:
    if not GOOD_FIXTURE.exists():
        fail(errors, "missing review-gate-smoke.good.md")
    else:
        good_errors = review_gate_trace_errors(read(GOOD_FIXTURE))
        if good_errors:
            fail(errors, f"review-gate-smoke.good.md should pass: {good_errors}")

    if not BAD_FIXTURE.exists():
        fail(errors, "missing review-gate-smoke.bad.md")
    else:
        bad_errors = review_gate_trace_errors(read(BAD_FIXTURE))
        if not bad_errors:
            fail(errors, "review-gate-smoke.bad.md should fail")


def smoke_temp_handoff_trace(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="ark-review-gate-smoke-") as tmp:
        root = Path(tmp)
        ark_dir = root / "docs" / "ark"
        ark_dir.mkdir(parents=True)
        handoff = ark_dir / "handoff.md"
        handoff.write_text(
            "\n".join(
                (
                    "<!-- ark-artifact: handoff -->",
                    "<!-- schema-version: 1.1 -->",
                    "<!-- last-updated: 2026-06-03 -->",
                    "",
                    "# Handoff",
                    "",
                    read(GOOD_FIXTURE),
                )
            ),
            encoding="utf-8",
        )
        trace_errors = review_gate_trace_errors(read(handoff))
        if trace_errors:
            fail(errors, f"temporary handoff trace should pass: {trace_errors}")


def main() -> int:
    errors: list[str] = []
    smoke_contract_assets(errors)
    smoke_fixtures(errors)
    if GOOD_FIXTURE.exists():
        smoke_temp_handoff_trace(errors)
    else:
        fail(errors, "cannot create temporary handoff trace without review-gate-smoke.good.md")

    if errors:
        print("ARK review gate smoke failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("ARK review gate smoke passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
