# Project Bootstrap Guidelines

本文件用于指导 `/ark-init` 的初始化行为。

## 核心目标

初始化一个现代、简洁、可维护的 Python 项目基础结构，适合个人开发并可逐步扩展。

## 模式选择

init 在执行前必须先确认项目模式：

### 模式 A：全新项目
项目从零开始，需要创建完整的项目骨架。适用于：
- 新项目初始化
- 早期仓库需要整理为标准结构

### 模式 B：已有项目
项目已存在，需要在现有结构上植入 ark 工作流。适用于：
- 接手已有项目
- 在现有代码库上启用 ark Artifact 工作流
- 项目已有代码但缺少工程化工作流

**模式 B 的核心差异：**
- 不创建任何代码文件或项目配置（pyproject.toml、src/、`<包名>/`、tests/ 等）
- 只创建工作流文件（CLAUDE.md、MEMORY.md、docs/ Artifact）
- CLAUDE.md 基于扫描到的真实项目结构动态生成
- 推荐在完成后执行 `/ark-analyze` 以理解代码库

## 必须交互确认的输入

以下内容应始终确认：

- project name：默认从当前目录名获取，需经过 Python 标识符合法性处理后确认
- target directory：默认当前目录

## 建议交互确认的输入

如果用户未提供，建议确认或主动给出默认值：

- Python 版本：默认 `3.12`，可选范围从 `3.10` 到 `3.14`
- 是否创建 pytest 测试（默认启用）

## 包管理工具

优先使用 **uv** 作为包管理工具。

- 如果 uv 可用，使用 uv 工作流
- 如果 uv 不可用，使用手动 fallback 工作流

## 项目名标准化规则

项目名必须经过 Python 标识符合法性处理：

1. 连字符 `-` 替换为下划线 `_`
2. 移除空格及其他特殊字符
3. 如果以数字开头，添加前缀 `_`
4. 全部转为小写

标准化后的项目名用于：
- `src/<project_name>/` 目录名
- `pyproject.toml` 中的 `name` 字段

## 目标目录结构

```
my_project/                  # 项目根目录
├── .github/                 # CI/CD 配置（可选）
│   └── workflows/
│       └── ci.yml
├── docs/                    # 文档 + ark Artifact
│   └── ark/                 # ARK 核心 Artifact
│       ├── spec.md
│       ├── design.md
│       ├── plan.md
│       ├── tasks.md
│       ├── decisions.md
│       ├── validation.md
│       └── handoff.md
├── src/                     # 源代码（src layout）
│   └── my_project/          # 包名目录
│       └── __init__.py      # 包初始化（仅含 __init__.py）
├── tests/                   # 测试目录
│   ├── __init__.py
│   └── conftest.py
├── pyproject.toml           # 核心配置文件
├── README.md                # 项目说明
├── CHANGELOG.md             # 变更日志
├── CLAUDE.md                # Claude Code 项目上下文
├── MEMORY.md                # ARK 框架规则入口
├── .gitignore
└── .venv/                   # 条件产物（由 uv 创建，不保证存在）
```

## 核心原则

### 1. 最小化初始化
- 除了 `__init__.py`，不创建其他 `.py` 文件
- 子目录不预先创建，按需由用户自行添加
- 让用户从空白开始填充业务逻辑

### 2. src layout
- 默认使用 `src/` layout
- 包名目录必须是合法的 Python 标识符

### 3. 双执行路径
- uv 可用路径：使用 uv 命令初始化
- uv 不可用路径：手动 fallback，创建基础文件
- 两条路径都确保项目可进入开发状态

### 4. 环境预检
- 检测 uv 是否可用
- 检测目标目录冲突
- 检测 Git 仓库状态

### 5. 模板 fallback 机制
- 模板文件存在时使用模板
- 模板文件不存在时使用内联 fallback 内容
- 不会因模板缺失而失败

### 6. 冲突处理
- 检测已存在的关键文件/目录
- 询问用户选择「覆盖」或「跳过」
- 跳过的文件不被覆盖

## 环境预检

### 检测 uv 可用性

```bash
uv --version
```

根据结果选择执行路径：
- uv 可用：记录版本号，使用 uv 工作流
- uv 不可用：记录原因，使用手动 fallback 工作流

### 检测目标目录冲突

扫描以下关键文件/目录：
- `pyproject.toml`
- `src/`
- `tests/`
- `docs/`

如果存在冲突，询问用户「覆盖」或「跳过」。

### 检测 Git 仓库状态

```bash
git rev-parse --is-inside-work-tree
```

- 已在仓库中：跳过 git init
- 不在仓库中：询问是否执行 git init

## uv 可用路径

```bash
uv init --no-workspace
说明：在 target directory 中原地初始化，不得额外嵌套一层目录
```

初始化后、`uv sync` 前，必须检查并补全 `pyproject.toml` 的 build-system 配置（src layout 需要）：
- 若缺少 `[build-system]`，追加 hatchling 配置
- 若缺少 `[tool.hatch.build.targets.wheel]`，追加 `packages = ["src/<project_name>"]`

```bash
uv venv
uv add pytest --dev  # 如启用测试
```

错误时记录状态，继续后续步骤。

## uv 不可用路径（手动 fallback）

1. 创建 `pyproject.toml`（最小版本，使用 hatchling）
2. 创建 `src/<project_name>/__init__.py`
3. 在摘要中标记需要手动完成的操作

## 文件创建顺序

1. 调整 `src/<project_name>/` 结构
2. 确保 `tests/` 结构正确
3. 创建 `.gitignore`（必须在 uv init 之后）
4. 创建 `README.md`
5. 创建 `CHANGELOG.md`
6. 创建 `CLAUDE.md`
7. 创建 `MEMORY.md`
8. 创建 `docs/` 及 7 个 Artifact
9. 执行 git init（如用户确认）

## .gitignore 创建

- 首选：使用 `${CLAUDE_PLUGIN_ROOT}/templates/project/gitignore-python.template` 模板
- 备选：使用内联 fallback 内容

**关键**：必须在 `uv init` 之后执行，避免被覆盖。

## CLAUDE.md

**自动创建，不需要用户确认。**

CLAUDE.md 是 Claude Code 进入项目时自动读取的上下文文件，用于：
- 让 Claude 快速了解项目结构
- 引导 Claude 使用 ARK Artifact 工作流
- 记录项目特定的编码规范

- 首选：使用 `${CLAUDE_PLUGIN_ROOT}/templates/project/CLAUDE.md.template` 模板
- 备选：使用内联 fallback 内容

模板文件存在时使用模板，不存在时使用内联 fallback 内容。

## MEMORY.md

**自动创建，不需要用户确认。**

MEMORY.md 是 Claude Code 的标准规则入口文件，Claude Code 会在每次对话开始时自动加载该文件。

- 首选：使用 `${CLAUDE_PLUGIN_ROOT}/templates/project/MEMORY.md.template` 模板
- 备选：使用内联 fallback 内容

模板文件存在时使用模板，不存在时使用内联 fallback 内容。

## Docs Artifact

**自动创建，不需要用户确认。**

docs/ Artifact 是 ark 实现跨会话记忆和状态追踪的核心，必须自动创建完整的 7 个 Artifact：

- `docs/ark/spec.md`
- `docs/ark/design.md`
- `docs/ark/plan.md`
- `docs/ark/tasks.md`
- `docs/ark/decisions.md`
- `docs/ark/validation.md`
- `docs/ark/handoff.md`

模板文件存在时使用模板，不存在时创建空文件。

## 模式 B 执行流程：已有项目

### 第一步：扫描项目

1. 扫描项目目录结构（排除 `.venv`、`venv`、`__pycache__`、`.git`、`node_modules`、`.mypy_cache`、`.pytest_cache`、`.ruff_cache`、`dist`、`build`、`*.egg-info`、`.tox`、`.nox`、`htmlcov`、`.coverage`、`.DS_Store`）。
2. 识别项目布局（src layout / flat / 其他）。
3. 识别包名和 Python 版本（从 `pyproject.toml` 或 `setup.py`）。
4. 识别技术栈（框架、关键依赖、工具链）。
5. 推断项目名：`pyproject.toml` 中的 `name` 字段 > 根目录下的包目录名 > 当前目录名。

### 第二步：生成 CLAUDE.md

基于扫描到的真实项目结构生成 `CLAUDE.md`，而非使用通用模板。

CLAUDE.md 应反映：
- 真实的项目结构和命令
- 真实的依赖和工具链
- 项目实际使用的测试命令
- ark Working Pattern（任务执行起始指引）

### 第三步：创建工作流文件

只创建以下文件（如不存在）；若文件存在但为空或仅含空行，视为可初始化对象：
- `docs/` 及 7 个空 Artifact
- `CLAUDE.md`（基于扫描结果生成）
- `MEMORY.md`

**不得创建或修改：**
- `pyproject.toml`、`setup.py` 等配置文件
- `src/`、`<包名>/`、`tests/` 等代码目录（无论何种 layout 均不触碰）
- `.gitignore` 等已有配置
- 任何已有代码文件

### 第四步：处理冲突

对已存在的工作流文件，询问用户：覆盖 / 跳过。

### 第五步：输出摘要

包含项目扫描结果和文件创建状态，推荐执行 `/ark-analyze`。

---

## 初始化哲学

- 优先最小可用结构
- 除了 `__init__.py`，不创建其他 `.py` 文件
- 子目录不预先创建
- 生成的文件应易读、易改
- 为后续迭代留下清晰起点
- uv 不可用时使用 fallback 确保流程完成
- 报告完整状态，让用户知道哪些需要手动处理

## 质量工具配置：变量探测规则

生成 ruff、pyright、settings.local.json 时，以下变量必须通过探测获取，不得硬编码。

### Python 版本

优先级（从高到低）：
1. `pyproject.toml` 的 `requires-python`（如 `>=3.11`）→ 取最低版本
2. `.python-version` 文件内容
3. `uv.lock` 或 `.venv` 中的信息
4. 默认 `3.11`

用途：`pyrightconfig.json` 的 `pythonVersion`、`pyproject.toml` 的 `target-version`

### 源码目录

优先级：
1. `pyproject.toml` 中已有的包/构建配置（如 `[tool.hatch.build.targets.wheel].packages`）
2. 实际存在的目录：检查 `src/`、`<package_name>/`、`app/`、`backend/`
3. 无法判断时，只 include 已确认存在的目录

用途：`pyrightconfig.json` 的 `include`、`pyproject.toml` 的 `[tool.ruff].src`

### 测试目录

检查 `tests/`、`test/`、`unit_tests/` 是否存在。不存在则不写入 include 列表。

### known-first-party

优先级：
1. `[project].name`（项目名中的 `-` 需替换为 `_`）
2. 实际 Python 包目录名
3. 无法确定时省略该字段

### 质量工具配置策略

质量工具的初始化分为两个独立阶段：**工具安装**和**配置生成**。两者必须分开处理，不得混淆。

#### 阶段一：工具安装

##### Mode A（全新项目）

默认自动安装，在 `uv sync` 之后执行：
- `uv add --dev ruff pyright`
- 作为项目默认开发质量工具链
- 如项目已有既定工具链，后续可替换

##### Mode B（已有项目）：检测 + 用户确认后安装

1. 检查 `pyproject.toml` 依赖（含 dev 依赖）是否包含 ruff 和 pyright
2. 若缺失，明确说明：后续 ARK 编码质量护栏（自动格式化、lint 修复、类型检查）会减弱
3. 提供选项：安装 Ruff + Pyright / 仅安装 Ruff / 跳过
4. **用户确认后才执行** `uv add --dev`
5. 安装工具不等于自动注入配置——配置仍遵循阶段二策略

**类型检查工具选择：** 当前默认安装 PyPI 包 `pyright`（Python wrapper，提供 `pyright` CLI 命令），团队如有其他偏好可替换。此为工具选型而非框架裁决，不写死为永久选择。输出中应明确表述为"通过 PyPI 包 pyright 安装"，不得仅写版本号，避免与 npm 官方路径混淆。

#### 阶段二：配置生成

##### Mode A（全新项目）：Bootstrap

直接生成：
- `.claude/ruff-hook.py`（从 `${CLAUDE_PLUGIN_ROOT}/scripts/ruff-hook.py` 复制到项目本地，hook 命令使用相对路径避免 `${CLAUDE_PLUGIN_ROOT}` 不展开的问题）
- `pyrightconfig.json`（基于探测变量）
- `.claude/settings.local.json`（本地配置，含 ruff hooks + permissions；hook 命令引用 `.claude/ruff-hook.py`）
- `pyproject.toml` 中追加 `[tool.ruff]` 配置（如不存在）

##### Mode B（已有项目）：Inspect & Respect

**文件分类：**

| 类别 | 文件 | Mode B 策略 |
|------|------|------------|
| ARK 工作流文件 | CLAUDE.md、MEMORY.md、docs/* | 可创建（如不存在） |
| 本地辅助配置 | .claude/ruff-hook.py、.claude/settings.local.json | 可创建（如不存在） |
| 项目质量配置 | pyrightconfig.json、pyproject.toml [tool.ruff] | 默认不创建，只报告建议 |

对 ARK 工作流文件和本地辅助配置执行三段式：

**A. 文件不存在** → 直接生成

**B. 文件存在且基本完整** → 不覆盖，报告：
- 检测到已有配置
- 跳过原因
- 建议用户检查哪些字段

**C. 文件存在但明显不完整** → 不覆盖，报告：
- 发现潜在问题（缺少哪些核心字段）
- 建议补充项

对项目质量配置（pyrightconfig.json、pyproject.toml [tool.ruff]），Mode B **不创建、不修改**，只报告检测结果和建议。

具体检测规则：

| 文件 | Mode B 行为 |
|------|------------|
| `pyrightconfig.json` | 不创建。检测是否存在及核心字段完整性，在摘要中报告探测结果和配置建议 |
| `.claude/ruff-hook.py` | 若需要生成或合并 `.claude/settings.local.json` 的 hooks，先将 `${CLAUDE_PLUGIN_ROOT}/scripts/ruff-hook.py` 复制到项目 `.claude/` 下；已存在且内容一致时跳过 |
| `.claude/settings.json` / `.claude/settings.local.json` | 检测是否含 `hooks.PostToolUse`。若均不存在，生成 `.claude/settings.local.json`（hook 命令引用 `.claude/ruff-hook.py`）；若 `settings.local.json` 已存在但缺 hooks，提供可选确认动作：将 ruff 文件级 hooks 合并追加（不覆盖已有字段，用户确认后执行）|
| `pyproject.toml [tool.ruff]` | 不追加。检测是否存在，在摘要中报告"建议手动补充"并列出可参考字段 |

**关于 Ruff src 范围：** Mode B 输出中的 Ruff 范围建议基于 init 阶段的轻量扫描，仅为初步探测结果。建议用户执行 `/ark-analyze` 后根据真实项目结构确认或补充完整范围（如加入 `tests/` 等）。

### 变量探测失败策略

当探测无法确定关键变量时，按以下策略退化：

| 变量 | 无法确定时的策略 |
|------|----------------|
| pythonVersion | 回退到 3.11，在摘要中标注"默认值，建议确认" |
| include dirs | 仅包含已确认存在的目录；若一个都无法确认，则不生成 pyrightconfig.json，在摘要中报告 |
| known-first-party | 直接省略该字段 |
| test dirs | 省略，不写入 include 列表 |