#!/usr/bin/env python3
"""End-to-end ARK artifact smoke using a minimal FastAPI hello endpoint."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_NAME = "hello-ark-api"
PACKAGE_NAME = "hello_ark_api"
HELLO_JSON = '{"message": "Hello, ARK!"}'
PYTEST_PACKAGES = ("fastapi==0.115.12", "pytest==8.3.5", "httpx==0.28.1")


def pytest_display_command() -> str:
    package_args = " ".join(f"--with {package}" for package in PYTEST_PACKAGES)
    return f"uv run --no-project --python {sys.executable} {package_args} pytest -q"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def require_tokens(errors: list[str], path: Path, tokens: tuple[str, ...]) -> None:
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            fail(errors, f"{path.name} missing token: {token}")


def ensure_absent(errors: list[str], path: Path, tokens: tuple[str, ...]) -> None:
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token in text:
            fail(errors, f"{path.name} contains forbidden token: {token}")


def create_fastapi_project(project: Path) -> None:
    write(
        project / "pyproject.toml",
        """[project]
name = "hello-ark-api"
version = "0.1.0"
requires-python = ">=3.9"
""",
    )
    write(project / "src" / PACKAGE_NAME / "__init__.py", "")
    write(
        project / "src" / PACKAGE_NAME / "main.py",
        """from fastapi import FastAPI


app = FastAPI()


@app.get("/hello")
def hello() -> dict[str, str]:
    return {"message": "Hello, ARK!"}
""",
    )
    write(
        project / "tests" / "test_hello.py",
        """from fastapi.testclient import TestClient

from hello_ark_api.main import app


def test_hello_endpoint() -> None:
    response = TestClient(app).get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, ARK!"}
""",
    )


def write_initial_artifacts(project: Path) -> None:
    ark = project / "docs" / "ark"
    write(
        ark / "spec.md",
        f"""<!-- ark-artifact: spec -->
<!-- schema-version: 1.1 -->
<!-- last-updated: 2026-06-03 -->

# Spec

## 用户可观察能力

用户调用 `GET /hello` 后，收到 JSON 问候消息 `{HELLO_JSON}`。

## 验收标准

- HTTP 状态码为 `200`。
- 响应 JSON 精确等于 `{HELLO_JSON}`。
- 该端点不依赖数据库、认证、配置文件或外部服务。

## 非范围

- 不做认证。
- 不做数据库。
- 不做参数化问候。
- 不做多语言。
""",
    )
    write(
        ark / "design.md",
        """<!-- ark-artifact: design -->
<!-- schema-version: 1.1 -->
<!-- last-updated: 2026-06-03 -->

# Design

## 技术方案

使用 FastAPI 暴露 `GET /hello`。应用入口为 `hello_ark_api.main:app`。

## 模块边界

- `hello_ark_api.main` 持有 FastAPI app 和 `/hello` 路由。
- `/hello` 只返回固定 JSON，不依赖外部服务。

## 技术闭环建议

最小 HTTP 闭环：通过 FastAPI `TestClient` 调用 `/hello`，验证状态码和 JSON 契约。
""",
    )
    write(
        ark / "plan.md",
        """<!-- ark-artifact: plan -->
<!-- schema-version: 1.1 -->
<!-- last-updated: 2026-06-03 -->

# Plan

## 目标

交付 FastAPI `/hello` 最小 HTTP 闭环。

## 阶段推进路径

| 阶段 | 交付单元 / 技术闭环 | 完成信号 |
|---|---|---|
| S1 | FastAPI `/hello` 最小 HTTP 闭环 | `uv run pytest` 通过，`GET /hello` 返回 `{"message": "Hello, ARK!"}` |

## 建议 task 边界

- T1 实现 FastAPI `/hello` 最小 HTTP 闭环。

## 不建议拆分为

- 创建 `main.py`
- 新增路由函数
- 新增测试文件
""",
    )
    write_ready_tasks(project)
    write(
        ark / "decisions.md",
        """<!-- ark-artifact: decisions -->
<!-- schema-version: 1.1 -->
<!-- last-updated: 2026-06-03 -->

# Decisions

## 当前长期决策

本 smoke 不记录长期不可逆决策。FastAPI 仅作为最小后端样例约束，细节保留在 `design.md`。
""",
    )
    write_initial_validation(project)
    write(
        ark / "handoff.md",
        """<!-- ark-artifact: handoff -->
<!-- schema-version: 1.1 -->
<!-- last-updated: 2026-06-03 -->

# Handoff

## 当前状态

FastAPI `/hello` 最小 HTTP 闭环已实现，等待验证记录闭合。

## 下一步

运行 `uv run pytest`，再由 `ark-validate` 写入 validation 证据。
""",
    )


def write_ready_tasks(project: Path) -> None:
    write(
        project / "docs" / "ark" / "tasks.md",
        """<!-- ark-artifact: tasks -->
<!-- schema-version: 1.1 -->
<!-- last-updated: 2026-06-03 -->

# Tasks

## Done

## Doing

## Ready for validation

- [ ] T1 实现 FastAPI `/hello` 最小 HTTP 闭环
  优先级：P0
  功能/技术闭环：用户调用 `GET /hello`，获得 `{"message": "Hello, ARK!"}`。
  实施要点：FastAPI app、`/hello` 路由、TestClient 契约测试。
  完成信号：`uv run pytest` 通过，HTTP 200 和 JSON 契约同时满足。
  完成后可观察结果：调用方可通过 HTTP 入口获得问候消息。
  真实性锚点：HTTP 入口
  真实闭环推进：建立 FastAPI `GET /hello` 公开契约。
  预期验证等级：L2
  建议验证方式：`uv run pytest`
  可与哪些任务合并验证：无
  仍未覆盖：真实 uvicorn/curl 手工 smoke
  下一步需要用户提供：无
  验证：待写入 validation.md

## Todo

## Blocked
""",
    )


def write_done_tasks(project: Path) -> None:
    write(
        project / "docs" / "ark" / "tasks.md",
        """<!-- ark-artifact: tasks -->
<!-- schema-version: 1.1 -->
<!-- last-updated: 2026-06-03 -->

# Tasks

## Done

- [x] T1 实现 FastAPI `/hello` 最小 HTTP 闭环
  优先级：P0
  功能/技术闭环：用户调用 `GET /hello`，获得 `{"message": "Hello, ARK!"}`。
  实施要点：FastAPI app、`/hello` 路由、TestClient 契约测试。
  完成信号：`uv run pytest` 通过，HTTP 200 和 JSON 契约同时满足。
  完成后可观察结果：调用方可通过 HTTP 入口获得问候消息。
  真实性锚点：HTTP 入口
  真实闭环推进：建立 FastAPI `GET /hello` 公开契约。
  预期验证等级：L2
  建议验证方式：`uv run pytest`
  可与哪些任务合并验证：无
  仍未覆盖：真实 uvicorn/curl 手工 smoke
  下一步需要用户提供：无
  验证：validation.md #验证记录 2026-06-03

## Doing

## Ready for validation

## Todo

## Blocked
""",
    )


def write_initial_validation(project: Path) -> None:
    write(
        project / "docs" / "ark" / "validation.md",
        """<!-- ark-artifact: validation -->
<!-- schema-version: 1.1 -->
<!-- last-updated: 2026-06-03 -->

# Validation

## 验证对象

T1 FastAPI `/hello` 最小 HTTP 闭环。

## 验证覆盖范围

- 覆盖任务：无，尚未执行验证。
- 覆盖原因：无。
- 未覆盖任务：T1
- 不覆盖原因：等待执行 `uv run pytest`。

## 已执行验证

无。

## 风险结论

- 当前验证强度：弱
- 当前可接受风险：无
- 当前不可接受风险：T1 尚未记录真实验证证据，不能标记 Done。
""",
    )


def write_validated_validation(project: Path, pytest_output: str) -> None:
    write(
        project / "docs" / "ark" / "validation.md",
        f"""<!-- ark-artifact: validation -->
<!-- schema-version: 1.1 -->
<!-- last-updated: 2026-06-03 -->

# Validation

## 验证记录 2026-06-03

### 验证对象

T1 FastAPI `/hello` 最小 HTTP 闭环。

预期响应：`GET /hello` 返回 `{HELLO_JSON}`。

### 验证覆盖范围

- 覆盖任务：T1
- 覆盖原因：同一 HTTP 真实入口
- 未覆盖任务：无
- 不覆盖原因：无

### 验证环境 / 前提

- 环境类型：本地
- 项目类型：backend service
- 真实性锚点：HTTP 入口
- 替身使用：FastAPI TestClient，不启动真实端口；真实 uvicorn/curl smoke 作为手工扩展项

### 已执行验证

| 验证项 | 方法 | 保真度 | 真实性锚点 | 替身使用 | 范围 | 结果 |
|---|---|---|---|---|---|---|
| `/hello` HTTP 契约 | `uv run pytest` | L2 | HTTP 入口 | TestClient | T1 | 通过 |

**执行命令与输出摘要：**
```text
uv run --no-project --python {sys.executable} --with fastapi==0.115.12 --with pytest==8.3.5 --with httpx==0.28.1 pytest -q
{pytest_output.strip()}
```

**检查结果归因：**
- 全量检查状态：通过
- 既有失败项：无
- 本次改动新增问题：未发现

## 风险结论

- 当前验证强度：中
- 当前可接受风险：未启动 uvicorn 真实端口，当前 smoke 只验证 TestClient HTTP 契约
- 当前不可接受风险：无
- 后续建议验证：release manual smoke 可补 `uvicorn` + `curl`
""",
    )


def check_initial_artifacts(project: Path, errors: list[str]) -> None:
    ark = project / "docs" / "ark"
    require_tokens(
        errors,
        ark / "spec.md",
        (
            "用户可观察能力",
            "GET /hello",
            HELLO_JSON,
            "验收标准",
            "非范围",
        ),
    )
    require_tokens(
        errors,
        ark / "design.md",
        ("FastAPI", "hello_ark_api.main:app", "/hello", "不依赖外部服务"),
    )
    require_tokens(
        errors,
        ark / "plan.md",
        (
            "阶段推进路径",
            "FastAPI `/hello` 最小 HTTP 闭环",
            "建议 task 边界",
            "不建议拆分为",
        ),
    )
    require_tokens(
        errors,
        ark / "tasks.md",
        (
            "T1 实现 FastAPI `/hello` 最小 HTTP 闭环",
            "功能/技术闭环",
            "完成信号",
            "真实性锚点：HTTP 入口",
            "建议验证方式：`uv run pytest`",
            "Ready for validation",
        ),
    )
    ensure_absent(errors, ark / "tasks.md", ("- [x] T1",))
    require_tokens(
        errors,
        ark / "validation.md",
        ("未覆盖任务：T1", "T1 尚未记录真实验证证据，不能标记 Done"),
    )
    ensure_absent(errors, ark / "spec.md", ("待填写", "标准 1", "问题 1"))


def check_ready_stage_contract(project: Path, errors: list[str]) -> None:
    tasks = (project / "docs" / "ark" / "tasks.md").read_text(encoding="utf-8")
    validation = (project / "docs" / "ark" / "validation.md").read_text(encoding="utf-8")
    if "## Ready for validation" not in tasks or "T1" not in tasks:
        fail(errors, "ready stage fixture missing T1 Ready for validation")
    if "覆盖任务：T1" in validation and "- [x] T1" in tasks:
        fail(errors, "ready stage fixture already looks closed")
    if "- [x] T1" in tasks:
        fail(errors, "ready stage fixture must not mark T1 Done")


def check_done_stage_contract(project: Path, errors: list[str]) -> None:
    tasks = (project / "docs" / "ark" / "tasks.md").read_text(encoding="utf-8")
    validation = (project / "docs" / "ark" / "validation.md").read_text(encoding="utf-8")
    if "- [x] T1" not in tasks:
        fail(errors, "done stage fixture missing T1 Done")
    if "validation.md #验证记录 2026-06-03" not in tasks:
        fail(errors, "done stage fixture missing validation reference")
    for token in (
        "覆盖任务：T1",
        "覆盖原因：同一 HTTP 真实入口",
        "未覆盖任务：无",
        "uv run --no-project --python",
        "Hello, ARK!",
        "当前验证强度：中",
    ):
        if token not in validation:
            fail(errors, f"validated stage fixture missing validation token: {token}")


def run_pytest(project: Path, cache: Path, errors: list[str]) -> str:
    uv = shutil.which("uv")
    if uv is None:
        fail(errors, "uv is required for ark-skill-smoke, but uv was not found on PATH")
        return ""

    env = os.environ.copy()
    env["UV_CACHE_DIR"] = str(cache)
    env["UV_PYTHON_INSTALL_DIR"] = str(cache.parent / "uv-python")
    env["PYTHONPATH"] = str(project / "src")
    command = [uv, "run", "--no-project", "--python", sys.executable]
    for package in PYTEST_PACKAGES:
        command.extend(("--with", package))
    command.extend(("pytest", "-q"))

    result = subprocess.run(
        command,
        cwd=project,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    output = (result.stdout + result.stderr).strip()
    if result.returncode != 0:
        fail(
            errors,
            "FastAPI hello endpoint pytest failed "
            f"(exit code {result.returncode}): {output}",
        )
    return output


def run_smoke(root: Path) -> list[str]:
    errors: list[str] = []
    project = root / PROJECT_NAME
    cache = root / "uv-cache"
    project.mkdir(parents=True)
    cache.mkdir()

    create_fastapi_project(project)
    write_initial_artifacts(project)
    check_initial_artifacts(project, errors)
    check_ready_stage_contract(project, errors)

    pytest_output = run_pytest(project, cache, errors)
    if not errors:
        write_validated_validation(project, pytest_output)
        write_done_tasks(project)
        check_done_stage_contract(project, errors)

    return errors


def print_failure_report(root: Path, project: Path, errors: list[str]) -> None:
    print("ARK skill smoke failed.")
    print("Failure summary:")
    for error in errors:
        print(f"- {error}")
    print("Failed command:")
    print(f"  {pytest_display_command()}")
    print("Temporary root kept for inspection:")
    print(root)
    print("Temporary project kept for inspection:")
    print(project)
    print("Temporary uv cache kept for inspection:")
    print(root / "uv-cache")
    print("Next steps:")
    print(f"- Inspect {project / 'docs' / 'ark' / 'tasks.md'}")
    print(f"- Inspect {project / 'docs' / 'ark' / 'validation.md'}")
    print("- Re-run the failed command from the temporary project directory after fixing the cause.")


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="ark-skill-smoke-"))
    project = root / PROJECT_NAME
    errors = run_smoke(root)

    if errors:
        print_failure_report(root, project, errors)
        return 1

    shutil.rmtree(root)
    print("ARK skill smoke passed.")
    print("Temporary project cleaned.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
