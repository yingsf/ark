# ark-init Fallback Templates

当模板文件（`${CLAUDE_PLUGIN_ROOT}/templates/project/`）不存在时，使用以下内联 fallback 内容。

---

## pyproject.toml（路径 B / uv 不可用时）

```toml
[project]
name = "<distribution_name>"
version = "0.1.0"
description = ""
requires-python = ">= <python_version>"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/<package_name>"]

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
ignore = ["E501", "RUF001", "RUF002", "RUF003"]

[tool.ruff.lint.isort]
known-first-party = ["<package_name>"]

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

PostToolUse hook 只执行文件级 `ruff format`。`ruff check --fix` 保留给 `/ark:ark-implement` 在批次完成等稳定点执行，不在每次编辑后自动运行。

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

# Claude Code local helper files (not committed by default)
.claude/
```

---

## README.md

````markdown
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

````markdown
# <project_name>

## Project Overview

<project_name> 是一个 Python 项目，使用 src layout，包名为 `<package_name>`。
本项目使用 ARK 框架管理开发流程，核心 Artifact 位于 `docs/ark/` 目录。

## ARK 项目画像
<!-- ark-init: 初始快照；后续由 ark-analyze / ark-sync 按真实项目演进建议更新 -->
- 项目类型：unknown
- 运行入口：待确认
- 真实性锚点：待确认
- 数据源：无 / 项目外部管理 / 本地路径元信息待确认（ARK 不托管数据内容）
- 外部依赖：无 / 待确认
- 契约边界：HTTP / MCP / CLI / SDK / 文件格式 / 事件 / 待确认
- 替身边界：mock/fake/in-memory 仅用于测试或短期替代，真实验证需单独记录

## Commands

文件级（日常编辑）：
```bash
uv run ruff format <file>
```

稳定点质量整理：
```bash
uv sync
uv run pytest
uv run pytest tests/test_xxx.py -v
uv run ruff check --fix .
uv run ruff format .
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

## Extension Docs

详细方案、专题设计、接口契约、集成说明、数据源元信息等不写入 `docs/ark/`。
按需使用 `/ark:ark-solution` 写入项目自有扩展文档：

- `docs/solution/`：专题详细方案
- `docs/design/`：模块或子系统详细设计
- `docs/contracts/`：HTTP/MCP/API/CLI/SDK/文件格式/事件契约
- `docs/integrations/`：外部系统接入
- `docs/data-sources/`：数据源元信息（不存放数据内容）

## Working Pattern

1. 开始任务前阅读 `docs/ark/tasks.md`，确认当前进展
2. 按对应 ARK Skill 的可写范围更新 Artifact；只读、说明或分流类 Skill 不落盘
3. 对涉及真实依赖、真实数据或公开契约的任务，优先建立最小真实闭环
4. 回复时说明：改了哪些文件、跑了哪些验证、哪些验证未执行

## Code Style

- 使用 type hints，所有公开函数必须有参数和返回值类型注解
- 注释详细度：fastchain-enhanced（核心路径详细，普通路径标准，简单路径克制）
- 公共类、公共函数、关键方法使用中文 Google 风格 docstring
- L2/L3 对象（核心 service / manager / provider / adapter、资源生命周期、外部依赖封装、启动链路、数据导入链路）使用增强 docstring，说明职责、设计原因、封装边界、生命周期和关键 Attributes
- 简单私有 helper、薄包装、简单 getter/setter 不强制补 docstring
- 不主动新增顶部模块级 docstring
- 不使用赋值语句后的三引号字符串说明常量、变量、集合或配置项；必要说明写在定义上方的中文块注释
- 复杂逻辑、边界条件、降级策略、资源生命周期、并发控制应补充中文注释
- 注释解释原因、约束和风险，避免重复代码表面含义
- 中文 docstring 和中文注释的描述句不使用句末中文终止标点（避免 `。`、`！`、`？`、`；`）
- 业务解释类注释优先写在代码上方，不写解释性尾随注释
- 导入顺序：stdlib → third-party → local，之间用空行分隔
- 优先使用 `pathlib.Path` 而非 `os.path`
- 异常处理不要裸 `except:`，至少捕获 `Exception`

## Do NOT

- 不要把 mock/fake/in-memory/合成数据结果描述为真实验证通过
- 不要把敏感数据、密钥、连接串或大体量数据内容写入 ARK 文档
````

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
- `${CLAUDE_PLUGIN_ROOT}/rules/capability-policy.md` - 能力降级策略
- `${CLAUDE_PLUGIN_ROOT}/rules/project-reality-policy.md` - 项目画像、真实性锚点与验证保真度
- `${CLAUDE_PLUGIN_ROOT}/rules/extension-doc-policy.md` - 扩展文档承载规则
- `${CLAUDE_PLUGIN_ROOT}/rules/artifact-placeholder-policy.md` - Artifact 模板占位与实质性内容判定
- `${CLAUDE_PLUGIN_ROOT}/rules/sub-agent-protocol.md` - Sub-agent 写权限隔离
- `${CLAUDE_PLUGIN_ROOT}/rules/external-review-gate.md` - 跨智能体外部审查门禁
- `${CLAUDE_PLUGIN_ROOT}/rules/task-sizing-summary.md` - 任务规模快速判断

## 使用说明

1. 以上规则文件定义了 ARK 框架的工作方式和约束
2. 执行 `/ark` 命令时，应遵循这些规则
3. 本 MEMORY.md 由用户维护，不自动覆盖；其引用的插件规则文件随插件更新生效
4. 完整的详细规则见：
   - `${CLAUDE_PLUGIN_ROOT}/rules/artifact-update-policy.md`（Artifact 回写完整协议）
   - `${CLAUDE_PLUGIN_ROOT}/rules/task-sizing-rules.md`（任务规模完整规则）
```

---

## AGENTS.md

```markdown
# <project_name>

## Project Overview

<project_name> 是一个 Python 项目，使用 src layout，包名为 `<package_name>`。
本项目使用 ARK 框架管理开发流程，核心 Artifact 位于 `docs/ark/` 目录。

## ARK 项目画像
<!-- ark-init: 初始快照；后续由 ark-analyze / ark-sync 按真实项目演进建议更新 -->
- 项目类型：unknown
- 运行入口：待确认
- 真实性锚点：待确认
- 数据源：无 / 项目外部管理 / 本地路径元信息待确认（ARK 不托管数据内容）
- 外部依赖：无 / 待确认
- 契约边界：HTTP / MCP / CLI / SDK / 文件格式 / 事件 / 待确认
- 替身边界：mock/fake/in-memory 仅用于测试或短期替代，真实验证需单独记录

## ARK In Codex

- 当前 Codex 环境应安装 ARK 插件；Skill 正文、规则文件和 Artifact 模板由插件提供
- 使用自然语言触发 ARK Skill，例如“使用 ARK 查看当前项目状态”、“按 ark-init 接入已有项目”、“使用 ark-plan 拆解这个需求”
- 不依赖 Claude Code 的 `/ark:ark-*` 斜杠命令；当文档提到 `/ark:ark-plan` 时，在 Codex 中等价表达为“使用 ark-plan”
- 不要在本文件中写入某台机器的插件安装绝对路径；跨机器恢复时以当前环境安装的 ARK 插件为准

## Commands

文件级（日常编辑）：
```bash
uv run ruff format <file>
```

稳定点质量整理：
```bash
uv sync
uv run pytest
uv run ruff check --fix .
uv run ruff format .
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
2. 按对应 ARK Skill 的可写范围更新 Artifact；只读、说明或分流类 Skill 不落盘
3. 对涉及真实依赖、真实数据或公开契约的任务，优先建立最小真实闭环
4. 回复时说明：改了哪些文件、跑了哪些验证、哪些验证未执行
```

---

## tests/conftest.py

```python
```

---

## docs/ Artifact 初始内容

所有 7 个 Artifact（spec.md、design.md、plan.md、tasks.md、decisions.md、validation.md、handoff.md）
在模板文件存在时，使用 `${CLAUDE_PLUGIN_ROOT}/templates/artifacts/` 下对应模板。

模板文件不存在时，必须使用以下最小 fallback 内容。fallback Artifact 不得为空，且必须保留 `ark-artifact`、`schema-version`、`last-updated` 版本头。

### spec.md

```markdown
<!-- ark-artifact: spec -->
<!-- schema-version: 1.1 -->
<!-- last-updated: YYYY-MM-DD -->

# Spec

## 背景
<!-- 待填写 -->

## 核心命题与不变量
<!-- 待填写 -->

## 目标
<!-- 待填写 -->

## 范围
<!-- 待填写 -->

## 非目标
<!-- 待填写 -->

## 真实性与数据要求
<!-- 待填写；不得写入数据内容 -->

## 验收标准
<!-- 按用户可观察能力、业务闭环、公开契约或真实入口结果表达，不得写成文件/函数级实现步骤 -->

## 开放问题
<!-- 待填写 -->
```

### design.md

```markdown
<!-- ark-artifact: design -->
<!-- schema-version: 1.1 -->
<!-- last-updated: YYYY-MM-DD -->

# Design

## 问题陈述
<!-- 待填写 -->

## 核心命题承接
<!-- 待填写 -->

## 方案概述
<!-- 待填写 -->

## 模块 / 组件结构
<!-- 待填写 -->

## 数据流 / 调用流
<!-- 待填写 -->

## 接口边界
<!-- 待填写 -->

## 真实依赖与替身边界
<!-- 待填写 -->

## 技术闭环建议
<!-- 提供给 plan/tasks 的技术闭环边界，不写文件/函数级执行步骤 -->
- 最小可运行闭环：
- 最小契约验证：
- 真实依赖 / 数据接入顺序：
- 不建议拆分为 task 的低层实现点：

## 扩展文档索引
<!-- 无 -->

## 风险与权衡
<!-- 待填写 -->
```

### plan.md

```markdown
<!-- ark-artifact: plan -->
<!-- schema-version: 1.1 -->
<!-- last-updated: YYYY-MM-DD -->

# Plan

## 目标
<!-- 待填写 -->

## 核心命题与范围保障
<!-- 待填写 -->

## 范围
<!-- 待填写 -->

## 非范围
<!-- 待填写 -->

## 真实性锚点与最小闭环
<!-- 待填写 -->

## 阶段推进路径
<!-- 阶段目标和交付单元按功能/技术闭环表达，不按文件、函数、配置项拆分 -->

| 阶段 | 目标 | 交付单元 / 技术闭环 | 入口条件 | 完成信号 | 真实性锚点 | 建议 task 边界 | 不建议拆分为 | 状态 |
|------|------|--------------------|---------|---------|------------|----------------|--------------|------|

## 风险
<!-- 待填写 -->

## 阻塞项
<!-- 当前无 -->

## 验证策略
<!-- 待填写 -->

## 当前状态
<!-- Status: not started / in progress / blocked / done -->
```

### tasks.md

```markdown
<!-- ark-artifact: tasks -->
<!-- schema-version: 1.1 -->
<!-- last-updated: YYYY-MM-DD -->

# Tasks

<!-- 本文件跟踪当前阶段的功能交付单元和可验证技术闭环。低层文件、函数、配置或测试步骤默认写入“实施要点”，不要拆成独立 task。-->

## 任务格式

每条任务至少包含：

- 功能/技术闭环：
- 实施要点：
- 完成信号：
- 完成后可观察结果：
- 真实性锚点：
- 预期验证等级：
- 建议验证方式：
- 可与哪些任务合并验证：
- 验证：

## Done
<!-- 无 -->

## Doing
<!-- 无 -->

## Ready for validation
<!-- 无 -->

## Todo
<!-- 待填写 -->

## Blocked
<!-- 无 -->
```

### decisions.md

```markdown
<!-- ark-artifact: decisions -->
<!-- schema-version: 1.1 -->
<!-- last-updated: YYYY-MM-DD -->

# Decisions

<!-- 暂无决策记录 -->
```

### validation.md

```markdown
<!-- ark-artifact: validation -->
<!-- schema-version: 1.1 -->
<!-- last-updated: YYYY-MM-DD -->

# Validation

## 验证对象
<!-- 待填写 -->

## 验证覆盖范围
- 覆盖任务：
- 覆盖原因：同一功能闭环 / 同一 batch / 同一真实入口 / 同一公开契约
- 未覆盖任务：
- 不覆盖原因：

## 已执行验证
<!-- 无 -->

## 未覆盖内容
<!-- 待填写 -->

## 建议验证但未执行
<!-- 待填写 -->

## 暂时无法验证项
<!-- 待填写 -->

## 风险结论
<!-- 待填写 -->
```

### handoff.md

```markdown
<!-- ark-artifact: handoff -->
<!-- schema-version: 1.1 -->
<!-- last-updated: YYYY-MM-DD -->

# Handoff

## 当前目标
<!-- 待填写 -->

## 当前阶段
<!-- 待填写 -->

## 已完成
<!-- 无 -->

## 未完成
<!-- 待填写 -->

## 风险 / 阻塞
<!-- 无 -->

## 下一次必须继承的结论
<!-- 待填写 -->

## 恢复顺序
<!-- 待填写 -->

## 推荐下一步
<!-- 待填写 -->

## 推荐 Skill
<!-- 待填写 -->
```
