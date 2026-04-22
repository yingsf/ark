---
name: ark-init
description: |
  以交互方式初始化 Python 项目结构、基础工程配置以及 ark 工作流所需文件。
  触发时机：新项目开始时、早期仓库需要整理为标准结构时、已有项目需要植入 ark 工作流时。
  关键词：初始化、新项目、init、脚手架、项目结构、setup、创建项目。
version: "1.0"
---

# /ark-init

## 目标
以交互方式初始化 Python 项目结构、基础工程配置以及 ark 工作流所需文件，使项目能够以最小可用状态进入开发。

## 适用场景
- 新项目开始时
- 早期仓库需要整理为标准结构时
- 已有项目需要植入 ark 工作流时
- 需要建立可持续维护的 Python 后端脚手架时
- 希望从一开始就启用 ark 的 Artifact 工作流时

## 不适用场景
- 当前需求只是一个很小的局部改动（不需要完整工作流）
- 用户明确要求不在项目中添加任何文件

## 必须确认的输入
- project name：默认从当前目录名获取，需经过 Python 标识符合法性处理后确认
- target directory：默认当前目录

## 建议确认的输入
- Python version：默认 `3.12`，可选范围 `3.10`–`3.14`
- 是否创建 pytest 测试（默认启用）

## 输出文件
`.gitignore`、`pyproject.toml`、`README.md`、`CHANGELOG.md`、`CLAUDE.md`、`MEMORY.md`、
`src/<project_name>/__init__.py`、`tests/__init__.py`、`tests/conftest.py`（如启用测试）、
`docs/` 及 7 个核心 Artifact

> `.venv/` 由 uv 按需创建，不是保证产物。

## 相关 Artifact
自动创建完整的 7 个核心 Artifact：
`docs/spec.md`、`docs/design.md`、`docs/plan.md`、`docs/tasks.md`、
`docs/decisions.md`、`docs/validation.md`、`docs/handoff.md`

## 目标目录结构
```
my_project/
├── docs/
│   ├── spec.md
│   ├── design.md
│   ├── plan.md
│   ├── tasks.md
│   ├── decisions.md
│   ├── validation.md
│   └── handoff.md
├── src/
│   └── my_project/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   └── conftest.py
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── CLAUDE.md
├── MEMORY.md
├── .gitignore
└── .venv/                # 条件产物（由 uv 创建，不保证存在）
```

## 核心原则
- 除了 `__init__.py`，不要创建其他 `.py` 文件
- 包名目录必须是合法的 Python 标识符
- 优先使用 uv，不可用时使用手动 fallback 流程
- 模板文件存在时使用模板，不存在时使用 fallback 内容（见 references/）
- docs/ Artifact 必须自动创建，不需要用户确认

## 项目名标准化规则
1. 连字符 `-` 替换为下划线 `_`
2. 移除空格及其他特殊字符
3. 如果以数字开头，添加前缀 `_`
4. 全部转为小写

## 工作流

### 第零步：模式选择

询问用户项目当前状态：

- **模式 A（全新项目）**：从零开始创建新项目 → 继续第一步
- **模式 B（已有项目）**：项目代码已存在，需要植入 ark 工作流 → 跳至模式 B

> 若当前目录已检测到 `pyproject.toml` / `setup.py` / `setup.cfg`、`src/` 目录、`requirements*.txt`、根目录下包含 `__init__.py` 的包目录、`tests/`、或常见入口文件（`main.py` / `app.py` / `manage.py`），应主动建议模式 B。

---

以下为模式 A 的执行步骤（全新项目）：

### 第一步：环境预检
- 检测 uv 是否可用
- 检测目标目录冲突
- 检测 Git 仓库状态

### 第二步：交互确认
收集并确认项目名、目标目录、Python 版本、是否启用测试。

### 第三步：选择执行路径

**路径 A（uv 可用）**：
1. `uv init <project_name> --python <version>`（在 target directory 中原地初始化，不得额外嵌套一层目录）
2. 在 pyproject.toml 添加 pytest 依赖（如启用）
3. 创建 `src/<project_name>/__init__.py`
4. 创建 tests/ 结构（如启用）
5. `uv sync`
6. `uv add --dev ruff pyright`（安装默认开发质量工具到 dev 依赖）

**路径 B（uv 不可用）**：
1. 手动创建目录结构
2. 手动生成 pyproject.toml
3. 提示用户手动安装依赖

### 第四步：创建配置文件
按顺序创建：`.gitignore`（uv init 之后）→ `CLAUDE.md` → `MEMORY.md`

优先使用模板，不存在时使用内联 fallback（fallback 内容见 `references/fallback-templates.md`）

### 第四点五步：创建质量工具配置

基于探测变量（见 `references/project-bootstrap-guidelines.md` 的"变量探测规则"）生成以下文件：

1. **`.claude/ruff-hook.py`** — 将 `${CLAUDE_PLUGIN_ROOT}/scripts/ruff-hook.py` 复制到目标项目的 `.claude/` 目录下。这是 hook 命令的执行入口，使用本地副本避免 `${CLAUDE_PLUGIN_ROOT}` 变量不展开的 bug。
2. **`pyrightconfig.json`** — 替换 `<python_version>`、`<source_and_test_dirs>` 为探测值
3. **`.claude/settings.local.json`** — 本地配置，含 ruff hooks + permissions（最小白名单）；hook 命令引用 `.claude/ruff-hook.py`（相对路径）；已存在时合并追加（同 Mode B 逻辑：不覆盖已有字段，将缺失的 hooks 和 permissions 补充进去）
4. **`pyproject.toml` 中追加 `[tool.ruff]`** — 仅当不存在时追加，替换 `<python_version_short>`、`<project_name>`、`<source_and_test_dirs>`

模板路径：
- `${CLAUDE_PLUGIN_ROOT}/scripts/ruff-hook.py`（复制到项目 `.claude/` 下）
- `${CLAUDE_PLUGIN_ROOT}/templates/project/pyrightconfig.template.json`
- `${CLAUDE_PLUGIN_ROOT}/templates/project/claude-project-settings.template.json`
- `${CLAUDE_PLUGIN_ROOT}/templates/project/pyproject-ruff.snippet.toml`

### 第五步：处理冲突
对每个已存在的文件，询问用户：覆盖 / 跳过 / 中止。

### 第六步：创建 docs/ Artifact
自动创建 7 个核心 Artifact，使用模板或空文件，不需要用户确认。

### 第七步：初始化 Git
若目录不在 Git 仓库中，询问是否执行 `git init`。

### 第八步：输出结果摘要
见「固定输出格式」。

---

### 模式 B：已有项目

适用场景：项目代码已存在，需要在现有结构上植入 ark 工作流文件。

#### B-第一步：扫描现有项目
1. 扫描项目目录结构（排除 `.venv`、`venv`、`__pycache__`、`.git`、`node_modules`、`.mypy_cache`、`.pytest_cache`、`.ruff_cache`、`dist`、`build`、`*.egg-info`、`.tox`、`.nox`、`htmlcov`、`.coverage`、`.DS_Store`）。
2. 识别项目布局类型（src layout / flat / 其他）。
3. 识别包名和 Python 版本（从 `pyproject.toml` 或 `setup.py`）。
4. 识别技术栈（框架、关键依赖、工具链）。
5. 推断项目名：`pyproject.toml` 中的 `name` 字段 > 根目录下的包目录名 > 当前目录名。
6. 将扫描结果用于生成 `CLAUDE.md`。

#### B-第二步：创建工作流文件
只创建不存在的文件；若文件存在但为空或仅含空行，视为可初始化对象。不触碰已有代码结构。

**必须创建（如不存在）：**
- `docs/` 目录及 7 个核心 Artifact
- `CLAUDE.md`（基于扫描到的真实项目结构动态生成，不使用通用模板）
- `MEMORY.md`

**不触碰（任何情况下不得修改）：**
- `pyproject.toml`、`setup.py`、`setup.cfg` 等已有配置
- `src/`、`<包名>/`、`tests/` 等已有代码目录（无论何种 layout 均不触碰）
- `.gitignore` 等已有配置文件（除非用户明确要求补充）
- 任何已有代码文件

#### B-第三步：处理冲突
对每个已存在的工作流文件（`CLAUDE.md`、`MEMORY.md`、`docs/` 下的文件）：若非空则询问覆盖 / 跳过；若为空或仅含空行则直接初始化。

#### B-第三点五步：质量工具配置（Inspect & Respect）

对质量工具文件执行检测 → 报告 → 不覆盖策略。核心原则：**默认不创建项目质量配置，只报告建议**。

文件分类与具体行为详见 `references/project-bootstrap-guidelines.md` 的"质量工具配置策略"和"变量探测规则"章节。

摘要：
1. **`pyrightconfig.json`** — 不创建，仅报告探测结果和配置建议
2. **`.claude/ruff-hook.py`** — 若 `.claude/settings.local.json` 需要生成或合并 hooks，则先将 `${CLAUDE_PLUGIN_ROOT}/scripts/ruff-hook.py` 复制到项目 `.claude/` 下；已存在且内容一致时跳过
3. **`.claude/settings.local.json`** — 不存在时直接生成（hook 命令引用 `.claude/ruff-hook.py`）；已存在但缺少 `hooks.PostToolUse` 时，提供可选确认动作：将 ruff 文件级 hooks 合并追加到已有配置（不覆盖用户已有的 permissions 等字段，用户确认后才执行）
4. **`pyproject.toml [tool.ruff]`** — 绝不自动追加，仅报告建议

所有检测结果和跳过原因必须在输出摘要中体现。跳过原因应先说明 Mode B 制度分类（项目质量配置默认不创建），再补充具体仓库背景（如项目未纳入该文件等），不得以 gitignore 等非制度因素作为主判断依据。

#### B-第三点八步：质量工具安装检测

检测项目是否已安装质量工具（ruff、pyright），若缺失则主动告知影响并提供安装选项。

**检测方式：** 检查 `pyproject.toml` 的依赖（含 dev 依赖）是否包含 ruff 和 pyright。

**若检测到缺失：**
1. 明确说明：后续 ARK 编码质量护栏（自动格式化、lint 修复、类型检查）会减弱
2. 提供以下选项供用户选择：
   - 安装 Ruff + Pyright（`uv add --dev ruff pyright`）
   - 仅安装 Ruff（`uv add --dev ruff`）
   - 跳过（后续可手动安装）
3. 用户确认后才执行安装

**输出表述：** 若安装成功，应明确写"Pyright 工具已安装（通过 PyPI 包 pyright 提供 pyright CLI）"，不得仅写版本号，避免与 npm 官方路径混淆。

**安装后仍不自动注入配置：** 即使安装了工具，配置生成仍遵循 B-第三点五步的 Inspect & Respect 策略。

#### B-第四步：输出结果摘要
见「固定输出格式」中的模式 B 部分。

## 验证要求

**模式 A（全新项目）：**
- 包名必须是合法的 Python 标识符
- 除了 `__init__.py`，不应创建其他 `.py` 文件
- docs/ Artifact 必须自动创建
- uv 不可用或命令失败不应导致整个流程中断
- `.gitignore` 创建必须在 `uv init` 之后执行
- 冲突检测中用户选择「跳过」的文件不应被覆盖

**模式 B（已有项目）：**
- 不得修改任何已有代码文件或项目配置
- `CLAUDE.md` 必须基于真实项目结构生成
- docs/ Artifact 必须自动创建
- 冲突检测中用户选择「跳过」的文件不应被覆盖

**可接受失败（不阻断整体成功）：**
- uv 不可用但 fallback 创建成功
- `uv sync` 失败但项目骨架已生成
- git init 被用户跳过
- 部分工作流文件因冲突被跳过

## 停止条件
- 按所选模式，所有应创建的文件已完成创建或因冲突被明确跳过
- 关键结果已汇总给用户（固定输出格式已填写）
- 用户已获得明确的下一步建议

## 固定输出格式

### 模式 A（全新项目）

#### 1. 确认参数
列出最终使用的初始化参数。

#### 2. 执行结果
| 步骤 | 状态 |
|------|------|
| 项目结构 | 成功 / 失败（原因）/ 跳过 |
| git init | 成功 / 跳过 |
| .gitignore | 使用模板 / 使用 fallback |
| CLAUDE.md | 使用模板 / 使用 fallback |
| MEMORY.md | 使用模板 / 使用 fallback |
| docs/ Artifact | 使用模板 / 使用空文件 |
| 质量工具安装 | 已安装 / 跳过（原因）|

#### 3. 目录树
输出简洁的最终目录树。

#### 4. 下一步
- 如有待处理事项（uv 未安装等），优先列出手动操作指引
- 需求未定义：建议 `/ark-spec`
- 目标明确但需要拆解：建议 `/ark-plan`

### 模式 B（已有项目）

#### 1. 项目扫描摘要
- 项目布局类型
- 技术栈（框架、关键依赖）
- 包名与 Python 版本

#### 2. 执行结果
| 步骤 | 状态 |
|------|------|
| 项目扫描 | 成功 / 失败（原因）|
| CLAUDE.md | 基于 scan 生成 / 跳过（已存在）|
| MEMORY.md | 使用模板 / 跳过（已存在）|
| docs/ Artifact | 使用模板 / 使用空文件 / 跳过（已存在）|
| 质量工具安装 | 已安装 / 已存在 / 跳过（用户选择）|

#### 3. 下一步
- **强烈建议**：`/ark-analyze`（理解代码库并预填充 artifact）
- 若需求或改动目标尚不清晰：`/ark-intake`（澄清目标、范围、约束和推荐流程）
- 若目标已经明确且可以拆解推进：`/ark-plan`

## 备注
`/ark-init` 的目标是「生成可工作的起点」，不是「一次性生成最终项目」。
详细的 fallback 模板内容见 `references/fallback-templates.md`。
各文件的创建策略与初始化哲学见 `references/project-bootstrap-guidelines.md`。
