# ark-init Fallback Templates

当模板文件（`${CLAUDE_PLUGIN_ROOT}/templates/project/`）不存在时，使用以下内联 fallback 内容。

---

## pyproject.toml（路径 B / uv 不可用时）

```toml
[project]
name = "<project_name>"
version = "0.1.0"
description = ""
requires-python = ">= <python_version>"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/<project_name>"]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.11",        # 默认开发质量工具，如项目已有既定工具链可替换
    "pyright>=1.1.400",  # 默认开发质量工具，如项目已有既定工具链可替换
]
```

---

## pyproject.toml Ruff 配置片段（追加到已有 pyproject.toml）

仅在 `[tool.ruff]` 不存在时追加：

```toml
[tool.ruff]
target-version = "py<python_version_short>"
line-length = 100
src = <source_and_test_dirs>

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B", "SIM", "C4", "RUF"]
ignore = ["E501"]

[tool.ruff.lint.isort]
known-first-party = ["<project_name>"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "lf"
docstring-code-format = true
```

---

## pyrightconfig.json

```json
{
  "include": <source_and_test_dirs>,
  "exclude": [
    "**/__pycache__",
    "**/.pytest_cache",
    "**/.ruff_cache",
    "**/.mypy_cache",
    "**/.venv",
    "**/node_modules",
    "build",
    "dist"
  ],
  "venvPath": ".",
  "venv": ".venv",
  "pythonVersion": "<python_version>",
  "typeCheckingMode": "standard",
  "useLibraryCodeForTypes": true,
  "reportMissingImports": "error",
  "reportMissingTypeStubs": "warning",
  "reportUnknownVariableType": "none",
  "reportUnknownMemberType": "none",
  "reportUnknownArgumentType": "none",
  "reportUnknownParameterType": "none",
  "reportUnusedImport": "warning",
  "reportUnusedVariable": "warning"
}
```

---

## .claude/settings.local.json（Mode A / Mode B 统一）

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(uv run ruff format *)",
      "Bash(uv run ruff check --fix *)",
      "Bash(uv run pyright)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "timeout": 30,
            "command": "uv run python .claude/ruff-hook.py"
          }
        ]
      }
    ]
  }
}
```

---

## .gitignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
*.egg
dist/
build/

# Virtual environments
.venv/
venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Static analysis
.ruff_cache/
.pyright/

# Environment
.env
.env.local
```

---

## README.md

```markdown
# <project_name>

> TODO: Add project description.

## Development

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (recommended)
- Python >= <python_version>

### Setup

```bash
uv venv
uv sync
```

### Run Tests

```bash
uv run pytest
```
```

（如果未启用 pytest，省略 "Run Tests" 部分。）

---

## CHANGELOG.md

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
```

---

## CLAUDE.md

```markdown
# <project_name>

## Project Overview

<project_name> 是一个 Python 项目，使用 src layout，包名为 `<project_name>`。
本项目使用 ARK 框架管理开发流程，核心 Artifact 位于 `docs/ark/` 目录。

## Commands

文件级（日常编辑）：
```bash
uv run ruff format <file>
uv run ruff check --fix <file>
```

全项目级（手动整理时）：
```bash
uv sync
uv run pytest
uv run pytest tests/test_xxx.py -v
uv run ruff format .
uv run ruff check --fix .
uv run pyright
```

## Artifact Workflow

| 文件 | 何时更新 |
|------|----------|
| `docs/ark/spec.md` | 添加新功能前 |
| `docs/ark/design.md` | 架构变更时 |
| `docs/ark/plan.md` | 任务规划或阶段推进时 |
| `docs/ark/tasks.md` | 开始/完成任务时 |
| `docs/ark/decisions.md` | 做出技术选型时 |
| `docs/ark/validation.md` | 完成验证后 |
| `docs/ark/handoff.md` | 阶段暂停或会话结束前 |

## Working Pattern

1. 开始任务前阅读 `docs/ark/tasks.md`，确认当前进展
2. 改动完成后更新对应 Artifact（tasks / validation / decisions）
3. 回复时说明：改了哪些文件、跑了哪些验证、哪些验证未执行
```

---

## MEMORY.md

```markdown
# ARK Framework Rules

## 核心规则文件

请阅读并遵循以下规则：

- `${CLAUDE_PLUGIN_ROOT}/rules/ark.md` - ARK 核心定义与原则
- `${CLAUDE_PLUGIN_ROOT}/rules/user-preferences.md` - 用户偏好
- `${CLAUDE_PLUGIN_ROOT}/rules/python-backend-conventions.md` - 编码规范
- `${CLAUDE_PLUGIN_ROOT}/rules/artifact-roles.md` - Artifact 职责速查
- `${CLAUDE_PLUGIN_ROOT}/rules/task-sizing-summary.md` - 任务规模快速判断

## 使用说明

1. 以上规则文件定义了 ARK 框架的工作方式和约束
2. 执行 `/ark` 命令时，应遵循这些规则
3. 规则文件由用户手动维护，不自动更新
4. 完整的详细规则见：
   - `${CLAUDE_PLUGIN_ROOT}/rules/artifact-update-policy.md`（Artifact 回写完整协议）
   - `${CLAUDE_PLUGIN_ROOT}/rules/task-sizing-rules.md`（任务规模完整规则）
```

---

## tests/conftest.py

```python
```

---

## docs/ Artifact 初始内容

所有 7 个 Artifact（spec.md、design.md、plan.md、tasks.md、decisions.md、validation.md、handoff.md）
在模板文件不存在时创建为空文件。若模板文件存在，使用 `${CLAUDE_PLUGIN_ROOT}/templates/artifacts/` 下对应模板。
