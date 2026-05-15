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
- 项目类型画像：backend service / library SDK / CLI / frontend / data-AI / plugin / mixed / unknown（Mode A 需确认；Mode B 先扫描推断，必要时请用户确认）

## 输出文件
`.gitignore`、`pyproject.toml`、`README.md`、`CHANGELOG.md`、`CLAUDE.md`、`MEMORY.md`、
`src/<project_name>/__init__.py`、`tests/__init__.py`、`tests/conftest.py`（如启用测试）、
`docs/ark/` 及 7 个核心 Artifact

> `.venv/` 由 uv 按需创建，不是保证产物。

> `.claude/ruff-hook.py` 和 `.claude/settings.local.json` 是 Claude Code 本地辅助文件，默认被 `.gitignore` 忽略，不作为必须提交的项目产物。

## 相关 Artifact
自动创建完整的 7 个核心 Artifact：
`docs/ark/spec.md`、`docs/ark/design.md`、`docs/ark/plan.md`、`docs/ark/tasks.md`、
`docs/ark/decisions.md`、`docs/ark/validation.md`、`docs/ark/handoff.md`

扩展文档目录（如 `docs/solution/`、`docs/contracts/`、`docs/data-sources/`）不由 init 默认创建；仅在后续 `/ark:ark-solution` 按需生成。

## 目标目录结构
```
my_project/
├── docs/
│   └── ark/
│       ├── spec.md
│       ├── design.md
│       ├── plan.md
│       ├── tasks.md
│       ├── decisions.md
│       ├── validation.md
│       └── handoff.md
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

## 能力探测

初始化时检测并追加到项目 CLAUDE.md（控制在 5-8 行以内）：

```markdown
## ARK 能力快照
<!-- ark-init: 仅初始化时参考，运行时各 Skill 按需重新检查 -->
- git: <可用/不可用>
- uv: <可用/不可用, 版本>
- pytest: <可用/不可用>
- ruff: <可用/不可用>
- pyright: <可用/不可用>
```

Agent tool 可用性不在此时探测，由各 Skill 执行时检查工具集。运行时能力判断仍以当前 Skill 检查为准。

能力降级策略见 `${CLAUDE_PLUGIN_ROOT}/rules/capability-policy.md`。

Mode A（全新项目）：生成能力快照。
Mode B（已有项目）：若 CLAUDE.md 已存在，能力快照只在用户确认后更新；未确认时只在输出摘要中报告当前探测结果，不写文件。若 CLAUDE.md 不存在则正常生成。

## ARK 项目画像

初始化时应在 `CLAUDE.md` 中写入或建议写入轻量项目画像（见 `${CLAUDE_PLUGIN_ROOT}/rules/project-reality-policy.md`）：

```markdown
## ARK 项目画像
<!-- ark-init: 初始快照；后续由 ark-analyze / ark-sync 按真实项目演进建议更新 -->
- 项目类型：backend service / library SDK / CLI / frontend / data-AI / plugin / mixed / unknown
- 运行入口：待确认 / <实际入口>
- 真实性锚点：<最小真实闭环，例如服务启动 + 配置加载 + 核心 API 调用>
- 数据源：无 / 项目外部管理 / 本地路径元信息待确认（ARK 不托管数据内容）
- 外部依赖：无 / 待确认 / <数据库、搜索、第三方 API 等>
- 契约边界：HTTP / MCP / CLI / SDK / 文件格式 / 事件 / 待确认
- 替身边界：mock/fake/in-memory 仅用于测试或短期替代，真实验证需单独记录
```

Mode A 项目画像：
- 必须询问项目类型；若用户不确定，可写 `unknown`，并建议后续 `/ark:ark-analyze` 或 `/ark:ark-intake`
- 不得因为用户选择 data-AI 而创建 `data/` 目录；数据由项目管理
- 若是 library/CLI 等无外部基础设施项目，真实性锚点应围绕安装、导入、命令执行或公开契约，而不是数据库

Mode B 项目画像：
- 基于实际文件推断项目类型、入口、依赖、数据源信号和契约边界
- 若 `CLAUDE.md` 已存在且非空，未获确认不得静默追加；只在输出中建议追加"ARK 项目画像"章节
- 推断必须标注不确定项，不得把目录名暗示写成确定结论

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

模板占位符统一使用 `<project_name>`。生成项目文件时必须替换所有 `<project_name>`、`<python_version>`、`<python_version_short>` 和 `<source_and_test_dirs>`，不得混用花括号占位符格式。

## 工作流

### 第零步：模式选择

自动检测当前目录的项目状态，输出检测结果并使用编号选择确认：

```
当前目录检测结果：
[列出检测到的项目文件，或"未检测到已有项目文件"]

请选择初始化模式：
1. 模式 A — 全新项目（从零开始创建）
2. 模式 B — 已有项目（植入 ark 工作流）[如检测到项目文件则标记为推荐]
```

检测规则：若当前目录存在以下任一文件/目录，标记为"检测到已有项目"：`pyproject.toml` / `setup.py` / `setup.cfg`、`src/` 目录、`requirements*.txt`、根目录下包含 `__init__.py` 的包目录、`tests/`、或常见入口文件（`main.py` / `app.py` / `manage.py`）。检测到时模式 B 标记为推荐。

---

以下为模式 A 的执行步骤（全新项目）：

### 第一步：环境预检
- 检测 uv 是否可用
- 检测目标目录冲突
- 检测 Git 仓库状态

### 第二步：交互确认
收集并确认项目名、目标目录、Python 版本、是否启用测试、项目类型画像。

### 第三步：选择执行路径

**路径 A（uv 可用）**：
1. `uv init <project_name> --python <version>`（在 target directory 中原地初始化，不得额外嵌套一层目录）
2. 在 pyproject.toml 添加 pytest 依赖（如启用）
3. 创建 `src/<project_name>/__init__.py`
4. 创建 tests/ 结构（如启用）
5. 确保 `pyproject.toml` 包含正确的 build-system 配置（src layout 需要）：若缺少 `[build-system]` 则追加 hatchling 配置，若缺少 `[tool.hatch.build.targets.wheel]` 则追加 `packages = ["src/<project_name>"]`
6. `uv sync`
7. `uv add --dev ruff pyright`（安装默认开发质量工具到 dev 依赖）

**路径 B（uv 不可用）**：
1. 手动创建目录结构
2. 手动生成 pyproject.toml
3. 提示用户手动安装依赖

### 第四步：创建配置文件
按顺序创建：`.gitignore`（uv init 之后）→ `CLAUDE.md` → `MEMORY.md`

优先使用模板，不存在时使用内联 fallback（fallback 内容见 `references/fallback-templates.md`）

### 第四点五步：创建质量工具配置

基于探测变量（见 `references/project-bootstrap-guidelines.md` 的"变量探测规则"）生成以下文件：

1. **`.claude/ruff-hook.py`** — 将 `${CLAUDE_PLUGIN_ROOT}/scripts/ruff-hook.py` 复制到目标项目的 `.claude/` 目录下。这是文件级 format hook 的执行入口，只执行 `ruff format`，使用本地副本避免 `${CLAUDE_PLUGIN_ROOT}` 变量不展开的 bug。
2. **`pyrightconfig.json`** — 替换 `<python_version>`、`<source_and_test_dirs>` 为探测值
3. **`.claude/settings.local.json`** — 本地配置，含 ruff format hook + permissions（最小白名单）；hook 命令引用 `.claude/ruff-hook.py`（相对路径）；已存在时合并追加（同 Mode B 逻辑：不覆盖已有字段，将缺失的 hooks 和 permissions 补充进去）
4. **`pyproject.toml` 中追加 `[tool.ruff]`** — 仅当不存在时追加，替换 `<python_version_short>`、`<project_name>`、`<source_and_test_dirs>`

`.claude/` 目录默认由 ARK `.gitignore` 模板忽略。不得提示用户必须提交 `.claude/ruff-hook.py` 或 `.claude/settings.local.json`；若团队确实需要共享 Claude Code 配置，应由用户显式调整 `.gitignore`。
不得为了让 `.claude/` 文件在 `git status` 中可见而移除或绕过 `.gitignore` 中的 `.claude/` 忽略规则。

模板路径：
- `${CLAUDE_PLUGIN_ROOT}/scripts/ruff-hook.py`（复制到项目 `.claude/` 下）
- `${CLAUDE_PLUGIN_ROOT}/templates/project/pyrightconfig.template.json`
- `${CLAUDE_PLUGIN_ROOT}/templates/project/claude-project-settings.template.json`
- `${CLAUDE_PLUGIN_ROOT}/templates/project/pyproject-ruff.snippet.toml`

### 第五步：处理冲突
对每个已存在的文件，询问用户：覆盖 / 跳过 / 中止。

### 第六步：创建 docs/ Artifact
自动创建 7 个核心 Artifact，使用模板或空文件，不需要用户确认。

每个 Artifact 顶部必须包含版本头注释：
```
<!-- ark-artifact: <name> -->
<!-- schema-version: 1.1 -->
<!-- last-updated: YYYY-MM-DD -->
```

模板文件中已包含版本头，使用模板时无需额外添加。使用空文件或 fallback 时需手动写入版本头。

模板映射：
- `spec.md` → `templates/artifacts/spec.template.md`
- `design.md` → `templates/artifacts/design.template.md`
- `plan.md` → `templates/artifacts/plan.template.md`
- `tasks.md` → `templates/artifacts/tasks.template.md`
- `decisions.md` → `templates/artifacts/decisions.template.md`
- `validation.md` → `templates/artifacts/validation.template.md`
- `handoff.md` → `templates/artifacts/handoff.template.md`

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
6. 观察已有代码中的 docstring 和注释风格（语言、是否使用 Google 风格、公共接口说明充分度），只做轻量采样，不批量改代码。
7. 识别项目类型、运行入口、外部依赖、契约边界和数据源信号；数据源只记录元信息，不读取或复制数据内容。
8. 将扫描结果用于生成 `CLAUDE.md`。

#### B-第二步：创建工作流文件
只创建不存在的文件；若文件存在但为空或仅含空行，视为可初始化对象。不触碰已有代码结构。

**必须创建（如不存在）：**
- `docs/` 目录及 7 个核心 Artifact（每个顶部含版本头注释）
- `CLAUDE.md`（基于扫描到的真实项目结构动态生成，不使用通用模板）
- `MEMORY.md`（使用模板或 fallback，见 `references/fallback-templates.md`，不得自定义内容）

Mode B 生成 `CLAUDE.md` 时应遵循注释风格的 Inspect & Respect：
- 若现有项目已有明确 docstring / 注释风格，记录并延续该风格
- 若未观察到明确风格或风格混乱，写入 ARK 默认中文 Google 风格作为后续新增/修改代码的默认约定
- 若 `CLAUDE.md` 已存在且非空，不静默覆盖；只在输出摘要中建议可追加"Documentation & Comments"章节，用户确认覆盖或追加后才修改
- 若 `CLAUDE.md` 已存在且非空，不静默覆盖；只在输出摘要中建议可追加"ARK 项目画像"章节，用户确认后才修改
- 不批量修改任何已有源码注释

**不触碰（任何情况下不得修改）：**
- `pyproject.toml`、`setup.py`、`setup.cfg` 等已有配置
- `src/`、`<包名>/`、`tests/` 等已有代码目录（无论何种 layout 均不触碰）
- `.gitignore` 等已有配置文件（除非用户明确要求补充）
- 任何已有代码文件

#### B-第三步：处理冲突
对每个已存在的工作流文件（`CLAUDE.md`、`MEMORY.md`、`docs/` 下的文件）：若为空或仅含空行则直接初始化；若非空则询问处理方式。

- `CLAUDE.md`：覆盖 / 追加"Documentation & Comments"章节 / 追加"ARK 项目画像"章节 / 跳过
- 其他工作流文件：覆盖 / 跳过

追加章节只用于补充 Mode B 扫描得到的注释/docstring 风格约定或 ARK 项目画像，不得重写用户已有内容。

#### B-第三点五步：质量工具配置（Inspect & Respect）

对质量工具文件执行检测 → 报告 → 不覆盖策略。核心原则：**默认不创建项目质量配置，只报告建议**。

文件分类与具体行为详见 `references/project-bootstrap-guidelines.md` 的"质量工具配置策略"和"变量探测规则"章节。

摘要：
1. **`pyrightconfig.json`** — 不创建，仅报告探测结果和配置建议
2. **`.claude/ruff-hook.py`** — 若 `.claude/settings.local.json` 需要生成或合并 hooks，则先将 `${CLAUDE_PLUGIN_ROOT}/scripts/ruff-hook.py` 复制到项目 `.claude/` 下；该 hook 只执行 `ruff format`；已存在且内容一致时跳过
3. **`.claude/settings.local.json`** — 不存在时直接生成（hook 命令引用 `.claude/ruff-hook.py`）；已存在但缺少 `hooks.PostToolUse` 时，提供可选确认动作：将 ruff 文件级 hooks 合并追加到已有配置（不覆盖用户已有的 permissions 等字段，用户确认后才执行）
4. **`pyproject.toml [tool.ruff]`** — 绝不自动追加，仅报告建议

Mode B 不修改既有 `.gitignore`。若创建了 `.claude/` 本地辅助文件，但现有 `.gitignore` 未忽略 `.claude/`，只在输出摘要中建议用户按需添加 `.claude/`；不得自动追加，也不得提示必须提交这些文件。

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
- `CLAUDE.md` 应包含中文 Google 风格 docstring 与中文注释规范
- `CLAUDE.md` 应包含 ARK 项目画像；数据源只记录元信息，不创建或托管数据目录
- uv 不可用或命令失败不应导致整个流程中断
- `.gitignore` 创建必须在 `uv init` 之后执行
- 冲突检测中用户选择「跳过」的文件不应被覆盖

**模式 B（已有项目）：**
- 不得修改任何已有代码文件或项目配置
- `CLAUDE.md` 必须基于真实项目结构生成
- `CLAUDE.md` 必须体现注释风格扫描结果：延续既有风格，或在无明确风格时采用 ARK 默认中文 Google 风格
- `CLAUDE.md` 应生成或建议追加 ARK 项目画像，包含项目类型、运行入口、真实性锚点、外部依赖、契约边界和数据源元信息
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
| 项目画像 | 已写入 / 待确认 / unknown |

#### 3. 目录树
输出简洁的最终目录树。

#### 4. 下一步
- 如有待处理事项（uv 未安装等），优先列出手动操作指引
- 需求未定义：建议 `/ark:ark-spec`
- 目标明确但需要拆解：建议 `/ark:ark-plan`

### 模式 B（已有项目）

#### 1. 项目扫描摘要
- 项目布局类型
- 技术栈（框架、关键依赖）
- 包名与 Python 版本
- 项目类型画像：类型、运行入口、真实性锚点、外部依赖、契约边界、数据源元信息
- 注释/docstring 风格：已识别既有风格 / 未发现明确约定，采用 ARK 默认中文 Google 风格 / 未扫描（原因）

#### 2. 执行结果
| 步骤 | 状态 |
|------|------|
| 项目扫描 | 成功 / 失败（原因）|
| CLAUDE.md | 基于 scan 生成 / 追加注释风格章节 / 跳过（已存在）|
| MEMORY.md | 使用模板 / 跳过（已存在）|
| docs/ Artifact | 使用模板 / 使用空文件 / 跳过（已存在）|
| 质量工具安装 | 已安装 / 已存在 / 跳过（用户选择）|
| 能力探测 | 已写入 / 用户未确认，仅报告 / 跳过（原因）|
| 项目画像 | 已写入 / 用户未确认，仅报告 / 待后续 analyze |

#### 3. 下一步
- **强烈建议**：`/ark:ark-analyze`（理解代码库并预填充 artifact）
- 若需求或改动目标尚不清晰：`/ark:ark-intake`（澄清目标、范围、约束和推荐流程）
- 若目标已经明确且可以拆解推进：`/ark:ark-plan`

## 备注
`/ark:ark-init` 的目标是「生成可工作的起点」，不是「一次性生成最终项目」。
详细的 fallback 模板内容见 `references/fallback-templates.md`。
各文件的创建策略与初始化哲学见 `references/project-bootstrap-guidelines.md`。
