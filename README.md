<div align="center">

# ARK

**Artifact-driven Reactive Kernel**

[![Version](https://img.shields.io/badge/version-1.0.13-blue.svg)](https://github.com/yingsf/ark)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-green.svg)](https://code.claude.com/docs/en/setup)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-purple.svg)](https://docs.anthropic.com/en/docs/claude-code/plugins)
[![Codex Plugin](https://img.shields.io/badge/Codex-Plugin-0ea5e9.svg)](https://developers.openai.com/codex)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

面向 Python 工程项目的 Claude Code / Codex 工作流插件。ARK 用文件化 Artifact 管理需求、设计、计划、任务、决策、验证和交接状态，并通过项目画像与真实性锚点，让复杂开发任务可追踪、可验证、可中断恢复。

[安装](#安装) · [快速开始](#快速开始) · [Mode A](#mode-a全新项目) · [Mode B](#mode-b已有项目) · [工作流](#推荐工作流) · [Skill](#skill-一览) · [FAQ](#faq)

</div>

---

## ARK 是什么

ARK 是一套 **Artifact-first** 的 Claude Code / Codex 工程工作流。它不是一组松散 prompt，而是一套围绕项目文件持续维护状态的开发内核。

传统 AI 编程容易遇到这些问题：

- 对话上下文变长后，后期实现、debug、validate 质量下降
- 中断几天后，不知道上次做到哪里
- 实现说完成了，但没有验证证据
- 文档、计划、代码现实逐渐不一致
- 模糊需求被直接猜测执行

ARK 的处理方式是把关键状态落到项目文件中：

| Artifact | 作用 |
|----------|------|
| `docs/ark/spec.md` | 需求目标、范围、非目标、验收标准 |
| `docs/ark/design.md` | 技术设计、模块关系、重要权衡 |
| `docs/ark/plan.md` | 阶段划分、推进顺序、风险和验证策略 |
| `docs/ark/tasks.md` | 当前任务、优先级、状态和阻塞 |
| `docs/ark/decisions.md` | 高成本、长期性、可能被质疑的关键决策 |
| `docs/ark/validation.md` | 已执行验证、证据、未覆盖项和风险 |
| `docs/ark/handoff.md` | 下次恢复时最该读取什么、继续做什么 |

## 核心能力

- **23 个专责 Skill**：入口、初始化、澄清、分析、规划、扩展方案、实施、外部审查门禁、验证、恢复、阶段治理和文档各有明确边界。
- **自动路由倾向**：用户直接描述任务时，规则会优先引导 Claude 选择对应 ARK Skill；这是倾向，不是运行时强保证。
- **显式智能入口**：`/ark:ark` 会读取当前 Artifact 状态，判断阶段并推荐下一步。
- **Sub-agent 支持**：analyze/validate 可用只读或证据收集 agent，implement 可用 batch worker，并通过 write set 审计防止越界写入。
- **Artifact 可信度四态**：`fresh / stale / conflicting / unknown` 帮助判断文档是否还能作为执行依据。
- **项目画像与真实性锚点**：区分后端、库、CLI、数据/AI 等项目类型，推动 plan/tasks/implement 尽早进入真实运行闭环。
- **扩展文档承载层**：专题方案、详细设计、契约、集成和数据源元信息由 `ark-solution` 写入项目自有文档目录，保持 `docs/ark/` 简洁。
- **能力降级策略**：Agent tool、git、uv、pytest、ruff、pyright 不可用时，不中断工作流，但会在输出中说明降级影响。
- **Mode A / Mode B 初始化**：既能创建全新 Python 项目，也能以 Inspect & Respect 方式接入已有项目。
- **阶段治理**：`ark-stage` 支持多 MVP / 多阶段项目的阶段状态裁决、归档、继承提炼、carryover gate 和新阶段初始化。
- **fastchain-enhanced 中文注释规范**：implement 会按 L0-L3 分级为公共接口、关键方法、资源封装和核心链路补充服务长期维护的中文 docstring / 注释；Mode B 会先尊重既有项目风格。
- **验证硬边界**：`ark-validate` 只记录验证证据，不修改源码，不用 mock 结果冒充真实通过。

---

## 安装

### 前置要求

| 工具 | 要求 |
|------|------|
| Claude Code 或 Codex | 已安装对应插件宿主 |
| Git | 推荐安装，用于状态判断和 checkpoint |
| Python | 推荐 3.12；ARK 支持 3.10-3.14 的项目初始化参数 |

### Claude Code 安装

在 Claude Code 中执行：

```text
/plugin marketplace add yingsf/ark
/plugin install ark@ark
/reload-plugins
```

安装时可选择作用范围：

| 选项 | 含义 | 建议 |
|------|------|------|
| Install for you | 当前用户所有项目可用 | 推荐 |
| Install for this project | 项目内共享插件配置 | 团队统一使用时选择 |
| Install locally | 只在当前仓库、当前用户生效 | 试用时选择 |

### Codex 安装

Codex 使用仓库中的 `.codex-plugin/plugin.json` 加载插件，核心内容仍复用 `skills/`、`rules/`、`templates/` 和 `scripts/`。

推荐在 Codex App 中让 Codex 代为完成安装。新开一个 Codex thread，直接发送：

```text
请帮我安装 ARK Codex 插件：
1. 添加 marketplace：yingsf/ark
2. 在 Codex App 的插件界面中安装并启用 ARK
3. 安装完成后，新开或刷新 thread，让 ARK Skills 生效

如果命令行只能添加 marketplace、不能完成 plugin 安装，请继续使用 Codex App 自己的插件安装能力操作。
```

也可以只先添加 marketplace 来源，再回到 Codex App 插件界面安装并启用 ARK：

```bash
codex plugin marketplace add yingsf/ark
```

本地开发或调试时，可以添加本地 clone：

```bash
git clone https://github.com/yingsf/ark.git
cd ark
codex plugin marketplace add .
```

也可以在父目录中直接添加 clone 下来的目录：

```bash
git clone https://github.com/yingsf/ark.git
codex plugin marketplace add ./ark
```

> 注意：`codex plugin marketplace add ...` 只负责把 ARK 加入 marketplace 来源。在某些 Codex 版本中，由于插件结构或 App 安装流程限制，命令行可以添加 marketplace，但不能直接完成 plugin 安装。遇到这种情况时，不要手动复制插件目录，应让 Codex App 继续完成安装和启用。

Codex 会将 ARK 入口显示为 Skill，例如 `Ark: Ark`、`Ark: Ark Init`、`Ark: Ark Plan`。你可以在技能面板中选择对应入口，也可以直接用自然语言触发：

```text
使用 ARK 查看当前项目状态
按 ark-init 接入已有项目
使用 ark-plan 拆解这个需求
使用 ark-validate 记录验证结果
```

当文档中出现 Claude Code 的 `/ark:ark-*` 写法时，在 Codex 中对应选择 `Ark: ...` Skill 或使用上面的自然语言表达即可。

### 升级

Codex 中更新 marketplace：

```bash
codex plugin marketplace upgrade ark
```

Claude Code 中升级：

```text
/plugin marketplace update ark
/plugin update ark@ark
/reload-plugins
```

`/plugin marketplace update ark` 用于刷新 Claude Code marketplace listing；`/plugin update ark@ark` 才会更新 Claude Code 已安装插件。ARK 使用显式版本号发布，每次发布都会同步更新 `plugin.json`、`marketplace.json` 和 README badge；如果版本号未变，Claude Code 可能认为已安装版本就是最新版本并跳过更新。

升级插件不会自动覆盖项目内的 `CLAUDE.md`、`MEMORY.md`、`AGENTS.md` 或 `docs/ark/*`。插件规则文件会随插件更新生效；如果新版本引入了新的项目模板或工作流入口，可在项目中重新执行 ark-init，选择 Mode B 检查是否需要补齐。

### 卸载

```text
/plugin remove ark

# 如果不再需要 marketplace
/plugin marketplace remove ark
```

卸载插件不会删除项目中已经生成的 `docs/ark/`、`CLAUDE.md`、`MEMORY.md`、`AGENTS.md`、`.claude/` 等文件。如需从项目中完全移除 ARK，请手动删除这些项目文件。

---

## 快速开始

ARK 的日常使用不需要先背命令。项目通过初始化接入后，Claude Code 项目使用 `CLAUDE.md` + `MEMORY.md`，Codex 项目使用 `AGENTS.md`；在对应宿主加载项目上下文和 ARK 插件后，你可以直接描述任务，ARK 会根据 `rules/ark.md` 的路由倾向优先按对应 Skill 的规则处理。

Claude Code 中可使用显式 `/ark:ark-*` 命令来初始化项目、强制指定流程、排查路由未触发，或向团队演示 ARK 的工作方式。Codex 中可从技能面板选择 `Ark: Ark`、`Ark: Ark Init`、`Ark: Ark Plan` 等入口，也可使用自然语言等价触发，例如“使用 ark-init 初始化项目”、“使用 ark-next 判断下一步”。如果你同时安装了 superpowers 等其他工作流插件，建议在任务开头写“按 ARK 工作流...”，或先让 ARK 读取项目状态并推荐下一步，再按推荐继续。

### 全新项目

```text
/ark:ark-init
```

选择：

```text
1. 模式 A — 全新项目（从零开始创建）
```

随后选择宿主配置：

```text
1. Claude Code — 生成 CLAUDE.md + MEMORY.md
2. Codex — 生成 AGENTS.md
3. Both — 同时生成三者
```

初始化完成后，直接描述你要做的事：

```text
帮我设计一个用户登录功能
```

ARK 会倾向进入新需求流程：澄清目标、形成规格、设计方案、拆计划、实施和验证。你仍然可以在需要时显式指定入口：

```text
/ark:ark
/ark:ark-intake
```

### 已有项目

```text
/ark:ark-init
```

选择：

```text
2. 模式 B — 已有项目（植入 ARK 工作流）
```

初始化完成后，直接描述你的接手目标：

```text
帮我理解这个项目的结构，找出下一步该从哪里开始
```

ARK 会倾向先分析项目，再根据不确定项推荐确认 spec/design 或进入 plan。你也可以显式执行 `/ark:ark` 查看当前 Artifact 状态。

### 不确定下一步

```text
/ark:ark
```

`/ark:ark` 会读取 `docs/ark/` 下的 Artifact，输出项目状态、非 fresh 的 Artifact、活跃任务、阻塞项和推荐下一步。

---

## Mode A：全新项目

Mode A 适合从空目录开始创建 Python 工程项目。它会生成项目骨架、质量工具配置、ARK Artifact、项目画像和宿主项目上下文（Claude Code: `CLAUDE.md` + `MEMORY.md`；Codex: `AGENTS.md`）。

### 适用场景

- 新项目从零开始
- 早期实验项目需要整理为标准 Python 结构
- 希望一开始就启用 ruff、pyright、pytest 和 ARK Artifact 工作流

### 示例：创建全新 API 项目

假设当前目录为空：

```text
my-api/
```

在 Claude Code 中执行：

```text
/ark:ark-init
```

ARK 会先检测当前目录：

```text
当前目录检测结果：
- 未检测到 pyproject.toml / setup.py / src / tests / Python 包目录

请选择初始化模式：
1. 模式 A — 全新项目（从零开始创建）[推荐]
2. 模式 B — 已有项目（植入 ARK 工作流）
```

模式选择应在当前 `/ark:ark-init` 会话内以交互选项完成；选择后 ARK 继续执行对应流程，不需要另起一条消息手工输入"模式A"或"模式B"。

选择 Mode A 后，ARK 会要求确认核心参数：

```text
distribution name: my-api
package name: my_api
target directory: 当前目录
Python version: 3.12
是否创建 pytest 测试: 是
项目类型: backend service / library SDK / CLI / frontend / data-AI / plugin / mixed / unknown
```

Mode A 会要求确认项目类型；如果你选择 `unknown`，ARK 会优先建议 `/ark:ark-intake` 澄清目标和类型，而不是默认执行 `/ark:ark-analyze`。

### Mode A 会做什么

Mode A 的执行重点：

1. 检测 `uv`、Git 状态和目标目录冲突。
2. 使用 `uv init --bare` 原地生成干净的 `pyproject.toml`，不保留 uv 示例代码或 console script。
3. 手动创建 `src/<package_name>/` layout 和测试结构。
4. 补齐 hatch build 配置和默认开发质量工具：ruff、pyright。
5. 按宿主生成项目上下文：Codex 生成 `AGENTS.md`；Claude Code 生成 `CLAUDE.md` + `MEMORY.md`；Both 同时生成三者。
6. Claude Code 宿主会额外生成 `.claude/ruff-hook.py` 和 `.claude/settings.local.json` 本地辅助文件（默认被 `.gitignore` 忽略；hook 只做文件级格式化）。Codex 宿主由 ARK 插件自带的 Codex `PostToolUse` hook 调用同一个 `scripts/ruff-hook.py`，提供同等文件级格式化效果。
7. 创建 `docs/ark/` 下 7 个核心 Artifact。
8. 在 Artifact 顶部写入 schema 版本头。
9. 询问是否执行 `git init`。

如果你只想快速开始，读到这里即可；下面是 Mode A 的详细产物和初始化记录说明。

### Mode A 典型产物

```text
my-api/
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
│   └── my_api/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   └── conftest.py
├── .gitignore
├── AGENTS.md                      # Codex 宿主
├── CHANGELOG.md
├── pyproject.toml
├── pyrightconfig.json
└── README.md
```

如果宿主选择 Claude Code 或 Both，还会生成 Claude Code 项目上下文和本地辅助配置：

```text
my-api/
├── .claude/
│   ├── ruff-hook.py
│   └── settings.local.json        # Claude Code 本地辅助配置，默认不提交
├── CLAUDE.md
└── MEMORY.md
```

在 Codex 宿主下，`.claude/ruff-hook.py` 和 `.claude/settings.local.json` 不会生成；同等效果由 ARK 插件自带的 Codex `PostToolUse` hook 实现。该 hook 调用插件内已有的 `scripts/ruff-hook.py`，在 Codex 执行 `apply_patch` / `Edit` / `Write` 后，对本次改动的 Python 文件运行 `ruff format`。首次启用插件 hook 时，Codex 可能会要求在 `/hooks` 中审查并信任该 hook。

### Mode A 产物说明

每个核心 Artifact 顶部都会写入 `ark-artifact`、`schema-version` 和 `last-updated` 版本头，便于 `ark-sync` 判断旧项目状态。Mode A 还会在宿主项目上下文中记录一次初始化时的能力快照（Codex: `AGENTS.md`；Claude Code: `CLAUDE.md`）；后续 Skill 执行时仍会按需重新检查 git、uv、pytest、ruff、pyright 等能力。

更细的 Artifact 协议、版本头语义和初始化契约由 Skill/reference 文件维护，README 只保留使用入口。

### Mode A 后的推荐下一步

Mode A 完成后，推荐直接用自然语言开始开发：

```text
帮我加一个用户注册和登录功能
```

ARK 会把它当作新需求，倾向采用渐进流程：

```text
ark-intake → ark-spec → ark-design → ark-solution（按需）→ ark-plan
  → ark-tasks → ark-implement → ark-test → ark-validate
```

`ark-solution` 只在需要专题详细方案、接口契约、集成说明或数据源元信息时介入；简单功能可以跳过。

从 1.0.8 起，`ark-tasks` 默认按功能交付单元或可验证技术闭环拆分任务，不按文件、函数、类或配置项拆分。低层实现步骤会放入任务的实施要点；多个同闭环任务可以作为明确 batch 执行，并用同一条 validation 记录覆盖。

从 1.0.9 起，上游 Artifact 也按同一粒度协作：`ark-spec` 的验收标准按用户可观察能力、业务闭环或公开契约表达；`ark-design` 给出技术闭环建议，不生成执行清单；`ark-plan` 维护阶段推进路径、建议 task 边界和不建议拆分项。

从 1.0.10 起，`ark-implement` 的批次、Sub-agent、Checkpoint 和注释/docstring 细则拆入 references；默认报告继续聚焦功能结果、验收方式、验证状态和下一步行动，减少过程噪音。

从 1.0.11 起，`ark-review` 默认执行深度契约驱动代码审查：先提炼任务契约，再检查实现、测试、跨层口径、fail-closed 默认行为、安全输出和 craftsmanship，并把问题映射到后续 ARK Skill。

从 1.0.12 起，验证记录片段与 validation 覆盖契约保持一致，决策记录片段也降低了标题和日期占位残留风险。

从 1.0.13 起，`ark-review-gate` 支持跨智能体外部审查门禁：高风险 task 立即外部审查，低风险同闭环 task 可进入最多 3 个 task / 90 分钟 / 1 个功能闭环 / 500 行核心 diff 的小批量审查；外部 findings 可导入后交给 `ark-debug` 最小修复，修复后生成定向复检包，复检默认只检查上一轮 findings 和明显回归。

`ark-implement` 的默认报告会先输出功能结果：当前完成状态、任务状态建议、本次能力变化、用户或调用方如何触发、可观察结果、当前限制和用户验收方式；同时给出外部审查门禁建议，说明当前 task 应立即外部审查、进入低风险 batch，还是需要先同步状态。Reality Check、注释/docstring、Checkpoint、Sub-agent 等过程细节仅在影响判断时输出。

若初始化时项目类型选择为 `unknown` 或目标仍不清楚，推荐先执行 `/ark:ark-intake`。只有在目录中已有实质代码、或你明确希望分析已有代码时，Mode A 才建议 `/ark:ark-analyze`。

也可以描述更窄的任务：

| 你可以直接说 | ARK 倾向 |
|--------------|----------|
| “帮我加一个用户登录功能” | 新需求澄清与规划 |
| “这个接口返回 500，帮我修” | bug 定位与修复 |
| “继续上次的任务” | 读取 Artifact 并裁决下一步 |
| “检查这次改动有没有风险” | code review |
| “我不确定现在该做什么” | 读取项目状态并推荐下一步 |

显式命令适合在你想强制指定流程时使用：

```text
/ark:ark          # 查看状态和推荐下一步
/ark:ark-debug    # 强制进入 debug 流程
/ark:ark-review   # 强制进入 review 流程
```

---

## Mode B：已有项目

Mode B 适合把 ARK 接入已有代码库。它遵循 **Inspect & Respect**：先检查，再建议；默认不修改已有代码和项目质量配置。

### 适用场景

- 接手一个已有 Python 项目
- 在老项目上启用 ARK Artifact 工作流
- 希望 Claude Code 或 Codex 后续开发有稳定的状态文件
- 不希望初始化过程改动业务代码或现有工程配置

### 示例：接入已有 FastAPI 项目

假设当前目录已经存在：

```text
backend/
├── app/
│   ├── main.py
│   └── routers/
├── tests/
├── pyproject.toml
└── README.md
```

执行：

```text
/ark:ark-init
```

ARK 会检测到已有项目：

```text
当前目录检测结果：
- pyproject.toml
- app/
- tests/
- README.md

请选择初始化模式：
1. 模式 A — 全新项目（从零开始创建）
2. 模式 B — 已有项目（植入 ARK 工作流）[推荐]
```

模式选择应在当前 `/ark:ark-init` 会话内以交互选项完成；选择后 ARK 继续执行对应流程，不需要另起一条消息手工输入"模式A"或"模式B"。

选择 Mode B 后，ARK 会扫描项目布局、包名、Python 版本、关键依赖、项目类型画像、真实性锚点、数据源信号和已有质量工具。

如果你只想接入后继续开发，知道 Mode B 默认不改业务代码即可；下面是它会创建的文件、不会触碰的范围和输出示例。

### Mode B 会创建什么

如果文件不存在，Mode B 会创建：

```text
backend/
├── docs/
│   └── ark/
│       ├── spec.md
│       ├── design.md
│       ├── plan.md
│       ├── tasks.md
│       ├── decisions.md
│       ├── validation.md
│       └── handoff.md
├── CLAUDE.md
└── MEMORY.md
```

如果宿主选择 Codex，会创建或建议追加：

```text
backend/
├── docs/
│   └── ark/
│       ├── spec.md
│       ├── design.md
│       ├── plan.md
│       ├── tasks.md
│       ├── decisions.md
│       ├── validation.md
│       └── handoff.md
└── AGENTS.md
```

如果宿主选择 Both，会同时维护 `CLAUDE.md`、`MEMORY.md` 和 `AGENTS.md`。

它还可能创建 Claude Code 本地辅助文件：

```text
.claude/
├── ruff-hook.py
└── settings.local.json
```

`.claude/` 是本地辅助配置目录，默认被 ARK `.gitignore` 模板忽略，不作为必须提交的项目状态。Mode B 只有在用户确认后才会创建这些本地辅助文件。团队如需共享 Claude Code 配置，应显式讨论后再调整 `.gitignore`。

如果 `.claude/settings.local.json` 已存在且缺少 ARK hook，ARK 只会在用户确认后合并缺失的 hook/permissions，不覆盖已有字段。

Codex 宿主不创建 `.claude/` 本地辅助文件；Codex 的文件级 format hook 由已安装的 ARK 插件提供。

Mode B 创建 Artifact 时必须使用 ARK 模板；模板不可用时，fallback Artifact 仍必须包含 `ark-artifact`、`schema-version`、`last-updated` 版本头，不生成纯空文件。

### Mode B 默认不会做什么

Mode B 默认不修改：

- 任何已有业务代码
- `pyproject.toml`
- `setup.py`
- `setup.cfg`
- `requirements*.txt`
- `.gitignore`
- 已有 `src/`、`app/`、包目录或 `tests/`
- 已有质量工具配置

如果宿主上下文文件已存在（Claude Code: `CLAUDE.md`；Codex: `AGENTS.md`），能力快照只会在用户确认后更新；未确认时，ARK 只在输出摘要中报告当前探测结果，不写文件。

Mode B 会识别并建议写入 `ARK 项目画像`：项目类型、运行入口、真实性锚点、外部依赖、契约边界和数据源元信息。它不会创建或托管项目数据目录，数据是否提交 Git 仍由项目自己决定。

### Mode B 的注释风格策略

Mode B 会轻量采样已有代码中的 docstring 和注释风格：

- 已有项目风格明确时，后续 `/ark:ark-implement` 优先延续项目风格。
- 未发现明确约定或风格混乱时，ARK 默认采用 `fastchain-enhanced` 中文 Google 风格：核心路径详细，普通路径标准，简单路径克制；公共类、公共函数、关键方法写中文 docstring，资源封装、核心链路、复杂逻辑、边界条件、降级策略、资源生命周期和并发控制补中文注释。
- 中文 docstring 和中文注释的描述句默认不使用句末中文终止标点；业务解释类注释优先写在代码上方。
- 如果宿主上下文文件不存在，Mode B 生成的项目上下文会记录上述判断（Claude Code: `CLAUDE.md`；Codex: `AGENTS.md`）。
- 如果宿主上下文文件已存在，Mode B 不静默覆盖，只在输出摘要中建议可追加"Documentation & Comments"章节，用户确认后才修改。
- Mode B 不批量修改任何已有源码注释。

### Mode B 的质量工具策略

Mode B 会检测 ruff、pyright 等工具，但默认只报告建议：

| 项目 | Mode B 行为 |
|------|-------------|
| `pyrightconfig.json` | 不自动创建，只报告建议 |
| `pyproject.toml [tool.ruff]` | 不自动追加，只报告建议 |
| ruff / pyright 依赖 | 缺失时提示影响；只有确认项目由 uv / pyproject 管理时才提供 `uv add --dev` 安装选项 |
| Claude Code `.claude/settings.local.json` | 本地辅助配置；只有用户确认后才生成或合并缺失 hook，默认不提交 |
| Codex `PostToolUse` hook | 由已安装 ARK 插件提供，不写入项目 `.claude/` |

Mode B 会同时检查 `requirements*.txt`、`setup.cfg`、`tox.ini`、`noxfile.py`、`.pre-commit-config.yaml` 等既有工具链信号，不会把 `uv add --dev` 强加给使用其他包管理方式的项目。

### Mode B 后的推荐下一步

Mode B 的重点是先建立对现有项目的可靠认知。初始化后，推荐直接说：

```text
帮我分析这个已有项目的架构、入口和主要模块
```

ARK 会倾向进入 `ark-analyze`：扫描代码库，输出项目概览、模块地图、入口路径、外部接口和不确定项。它可以预填充 `spec.md` 和 `design.md`，但会标注为待人工确认。

接下来你可以继续用自然语言推进：

```text
确认一下这个项目当前实际支持哪些能力
根据刚才的分析，帮我制定后续重构计划
继续推进上次未完成的任务
```

如果自动路由未触发，或你想明确指定流程，可以手动调用：

```text
/ark:ark-analyze
/ark:ark-spec
/ark:ark-design
/ark:ark-solution
/ark:ark-plan
```

---

## 推荐工作流

ARK 不是强制线性流程。日常使用时，你可以直接描述目标；下面展示的是 ARK 倾向采用的 Skill 流程，而不是要求你逐条手工执行的命令清单。

### 新功能

```text
“帮我给系统加用户登录”
  ↓
ark-intake      # 澄清目标、范围、规模；不写 Artifact
  ↓
ark-spec        # 写入 spec.md
  ↓
ark-design      # 写入 design.md，维护全局设计摘要和扩展文档索引
  ↓
ark-solution    # 可选：写专题方案、接口契约、集成或数据源元信息
  ↓
ark-plan        # 写入 plan.md
  ↓
ark-tasks       # 写入 tasks.md
  ↓
ark-implement   # 分批实现，可用 sub-agent worker
  ↓
ark-test        # 补测试
  ↓
ark-review-gate # 可选：跨智能体外部审查门禁，生成 Codex 审查包或定向复检包
  ↓
ark-validate    # 记录验证证据
```

### Bug 修复

```text
“这个接口报错了，帮我定位并修复”
  ↓
ark-debug       # 收集现象、错误信息、复现步骤，定位根因
  ↓
ark-implement   # 最小修复
  ↓
ark-test        # 回归测试
  ↓
ark-validate    # 记录证据；失败时推荐回到 ark-debug
```

### 跨智能体外部审查

```text
ark-implement
  ↓
ark-review-gate status   # 判断 immediate / batch-candidate / batch-ready
  ↓
ark-review-gate prepare  # 生成给 Codex/其他 agent 的审查包
  ↓
外部智能体审查
  ↓
ark-review-gate import   # 导入 findings，分类为必须修复 / 可延期 / 不处理
  ↓
ark-debug                # 只修复必须修复项
  ↓
ark-review-gate recheck  # 生成定向复检包，只复检上一轮 findings
  ↓
ark-validate             # 记录本地验证和外部审查 evidence
```

`ark-review-gate` 的目的不是减少审查质量，而是减少低风险 task 的重复完整审查。高风险 task 立即外部审查；低风险、同一功能闭环内的 task 可以小批量审查，但最多 3 个 task、90 分钟、1 个功能闭环或 500 行核心 diff，任一上限达到即停下审查。

### 接手项目

```text
“帮我接手这个已有项目，先看懂架构”
  ↓
ark-analyze
  ↓
ark-spec        # 审查确认 analyze 反推的需求
  ↓
ark-design      # 审查确认 analyze 反推的设计
  ↓
ark-solution    # 如需要专题方案、契约、集成或数据源元信息
  ↓
ark-plan
```

### 专题方案 / 契约 / 数据源元信息

```text
“为资产导入链路写一个详细方案，并明确 API 契约和真实样例数据要求”
  ↓
ark-solution    # 写入 docs/solution、docs/contracts 或 docs/data-sources
  ↓
ark-design      # 如需同步全局设计摘要和扩展文档索引
  ↓
ark-plan        # 拆执行阶段，优先安排最小真实闭环
```

扩展文档是项目自有文档，不属于 `docs/ark/` 7 个核心 Artifact。ARK 不管理数据内容，只记录数据源元信息、脱敏状态、样例范围和验证证据。

### 中断恢复

```text
“继续上次的任务”
  ↓
ark-next          # 读取 handoff.md / tasks.md / plan.md，裁决下一步
  ↓
继续执行推荐的 Skill
  ↓
ark-handoff       # 需要收口或中断时，主动记录恢复点
```

### 阶段治理 / 多 MVP 切换

```text
“收口 S1，准备进入 S2”
  ↓
ark-stage         # 先审计当前阶段状态，检查 blocked / conflicting / stale
  ↓
preview           # 展示归档、新阶段重建、carryover gates 和风险确认项
  ↓
用户确认后写入
```

`ark-stage` 用于多 MVP 或大项目阶段切换。它会把当前 7 个核心 Artifact 原样归档到 `docs/ark/archive/<stage-id>/`，生成 `stage-summary.md`，维护 `docs/ark/stages.md`，并在开启新阶段时提炼长期不变量、设计约束、长期决策、验证基线和未覆盖风险。

其中 `docs/ark/decisions.md` 按项目级长期记忆处理：阶段收口只归档历史快照，开启新阶段时继续保留仍有效的长期决策；阶段性决策只在明确不再约束新阶段时留在 archive，不确定时默认保留，已被替代的长期决策标记为 `superseded` / 已替代。

除只读的 `stage-status` 外，`stage-close`、`stage-open` 和 `stage-transition` 都必须先输出 preview 并等待确认。若存在 Blocked、Ready for validation、Done 缺 validation、handoff 与 tasks 冲突，或 plan 当前状态过期，`ark-stage` 不得静默写成 `closed`；用户确认带风险进入下一阶段时，状态写为 `closed-with-risk`，并把未闭合项写入 Carryover Gates。

如果你怀疑文档已经过期，可以直接说：

```text
“先同步一下代码和 Artifact 状态，再告诉我下一步”
  ↓
ark-sync          # 同步 Artifact 与文件现实，识别 spec/design 是否过期或冲突
  ↓
ark-next
```

### spec/design 漂移处理

`spec.md` 和 `design.md` 是活文档，但正式写入仍由专责 Skill 完成：

- `ark-implement`：编码完成点识别本次实现是否改变需求范围、验收标准、外部接口、模块边界或运行机制；只建议 `/ark:ark-spec` / `/ark:ark-design`，不直接改 `spec.md` / `design.md`。
- `ark-debug`：修复后如果发现错误语义、边界条件或设计假设过期，也只建议对应 Skill。
- `ark-refactor`：若重构改变模块边界、依赖方向或资源生命周期，建议更新 `design.md`；若外部行为实际变化，先回到 spec/design 确认。
- `ark-sync`：事后做全局一致性校准，标记 `spec.md` / `design.md` 为 `stale` 或 `conflicting`，并推荐后续 Skill。
- `ark-spec` / `ark-design`：真正负责把确认后的需求或设计变化写入 Artifact。

### 扩展文档漂移处理

引入 `ark-solution` 后，ARK 同时检查扩展文档漂移：

- `ark-implement` / `ark-debug` / `ark-refactor`：发现专题方案、接口契约、集成或数据源元信息与实现不一致时，只建议 `/ark:ark-solution`。
- `ark-sync`：检查 `docs/ark/design.md` 的扩展文档索引和项目自有扩展文档，标记 `fresh / stale / conflicting / unknown`。
- `ark-design`：维护扩展文档索引和全局摘要，不复制扩展文档正文。
- `ark-solution`：负责扩展文档正文，不直接修改 `docs/ark/*`。

---

## 自动路由倾向

ARK 在 `rules/ark.md` 中定义了路由倾向。用户可以直接描述任务，Claude 会优先选择对应 Skill；如果自动触发未发生，会输出推荐入口。显式命令不是日常使用的唯一入口，而是强制指定流程的工具。

这项能力有一个前提：当前项目已经通过 `/ark:ark-init` 接入 ARK，并且当前宿主已经加载 ARK 规则（Claude Code: 项目 `MEMORY.md` 引用规则；Codex: 已安装 ARK 插件并读取项目 `AGENTS.md`）。ARK 不是全局运行时调度器；如果同一环境里安装了多个工作流插件，宿主可能受到其他规则影响。

在多插件环境中，如果你希望明确走 ARK，推荐这样描述：

```text
按 ARK 工作流，帮我加一个用户登录功能
```

或者先使用显式入口读取项目状态、查看推荐下一步，再按推荐继续：

```text
/ark:ark
```

| 用户意图 | 优先 Skill |
|----------|------------|
| 新需求、新功能、目标未澄清 | `ark-intake` |
| 专题方案、详细设计、接口契约、集成或数据源元信息 | `ark-solution` |
| 实现已有 plan/task/batch | `ark-implement` |
| bug、报错、异常、失败 | `ark-debug` |
| 继续、推进、不确定下一步 | `ark-next` |
| 外部审查、跨智能体审查、Codex review、审查门禁 | `ark-review-gate` |
| 审查、review、检查代码 | `ark-review` |
| 重构、优化结构 | `ark-refactor` |
| 文档、README、说明 | `ark-docs` |
| 体检、状态、同步 | `ark-sync` |
| 阶段收口、归档、进入下一 MVP | `ark-stage` |
| 分析项目、接手 | `ark-analyze` |
| 初始化、新项目 | `ark-init` |

常见自然语言输入：

```text
帮我加一个用户登录功能
这个 Mongo 查询偶尔报错，帮我定位
继续上次没完成的任务
检查这次改动有没有回归风险
同步一下代码和 Artifact 状态
```

显式入口仍然保留，适合在自动路由未触发、你想强制指定流程、或需要教学演示时使用：

```text
/ark:ark
/ark:ark-debug
/ark:ark-implement
```

---

## Skill 一览

| 分类 | Skill | 职责 |
|------|-------|------|
| 入口 | `/ark:ark` | 读取项目状态，推荐下一步 |
| 启动 | `/ark:ark-init` | 初始化全新项目或接入已有项目 |
| 说明 | `/ark:ark-helper` | 回答 ARK 用法、概念和通用流程 |
| 澄清 | `/ark:ark-intake` | 澄清目标、范围、规模和推荐流程；只分流与建议落盘，不直接写 Artifact |
| 分析 | `/ark:ark-analyze` | 读取代码库，建立架构认知，可预填充 spec/design |
| 规划 | `/ark:ark-spec` | 写需求规格和用户/业务/契约视角验收标准 |
| 规划 | `/ark:ark-design` | 写技术设计和技术闭环建议 |
| 规划 | `/ark:ark-solution` | 写专题方案、详细设计、接口契约、集成或数据源元信息 |
| 规划 | `/ark:ark-plan` | 写阶段推进路径、task 边界和验证策略 |
| 规划 | `/ark:ark-tasks` | 按功能交付单元或技术闭环拆分任务和状态 |
| 决策 | `/ark:ark-decide` | 记录重要工程决策 |
| 实施 | `/ark:ark-implement` | 最小可行实现，默认输出功能结果和验收方式，支持 batch 和 checkpoint；检查真实性锚点并识别 spec/design/extension 漂移 |
| 实施 | `/ark:ark-debug` | 定位 bug 根因，形成修复方案；识别修复暴露的需求/设计/扩展文档漂移 |
| 实施 | `/ark:ark-refactor` | 保持行为不变，改善结构；识别设计现实和扩展文档变化 |
| 审查 | `/ark:ark-review-gate` | 组织跨智能体外部审查门禁，判断立即审查或小批量审查，生成审查包、导入 findings 并生成定向复检包 |
| 审查 | `/ark:ark-review` | 深度契约驱动代码审查，检查实现、测试、风险和后续 ARK 路径 |
| 验证 | `/ark:ark-test` | 创建和组织测试 |
| 验证 | `/ark:ark-validate` | 记录验证证据，只验证不修复；同闭环任务可共享验证记录 |
| 恢复 | `/ark:ark-handoff` | 写入恢复点 |
| 恢复 | `/ark:ark-next` | 根据 Artifact 裁决下一步 |
| 恢复 | `/ark:ark-sync` | 检查并同步 Artifact、扩展文档与文件现实，标记过期或冲突 |
| 阶段 | `/ark:ark-stage` | 审计阶段状态，归档阶段 Artifact，维护 stages.md，提炼继承项并初始化新阶段 |
| 文档 | `/ark:ark-docs` | 更新 README 或其他项目说明 |

---

## Sub-agent 模式

ARK 会在 Medium/Large 任务中优先使用 sub-agent 缓解 context rot，但主 agent 始终是状态合并者。

| 场景 | sub-agent 角色 | 写权限 |
|------|----------------|--------|
| `ark-analyze` 阶段二/三扫描 | reader | 不写任何文件 |
| `ark-validate` 执行测试/脚本 | collector | 不写任何文件 |
| `ark-implement` batch 实施 | worker | 只写 batch write set 内的源文件 |
| `ark-solution` 专题文档编写 | writer | 只写明确分配的扩展文档 write set |

所有核心 Artifact 都由主 agent 统一写入。`ark-implement` 的 worker 完成后，主 agent 会检查 diff 是否超出 write set；越界时停止并报告，不自动合并。

Agent tool 不可用时，Skill 会退回单上下文执行，并在输出中记录：

```text
Sub-agent 状态：未启用
原因：当前环境未提供 Agent tool / 任务规模不需要 / 用户禁用
降级影响：context rot 风险较高，建议按 batch 收口，及时 handoff
```

---

## Artifact 可信度

ARK 使用四态判断 Artifact 是否还能作为执行依据：

| 状态 | 含义 | 示例 |
|------|------|------|
| `fresh` | 内容与文件现实、Artifact 之间关系和验证记录一致 | tasks.md 的 Doing 项与当前代码改动一致 |
| `stale` | 代码或任务状态已经变化，但 Artifact 未反映 | batch 2 已完成，但 tasks.md 仍停在 batch 1 |
| `conflicting` | Artifact 之间互相矛盾，或与文件现实冲突 | plan.md 的阶段顺序与 design.md 描述的模块关系冲突 |
| `unknown` | 缺少证据，或旧项目缺少 schema 版本头 | 接手旧项目时 Artifact 没有版本头，且无法确认是否仍有效 |

判断优先级：

1. 当前文件现实
2. Artifact 之间一致性
3. 已执行验证记录
4. `git diff` / `git log`（如可用）

无 Git 项目仍可依据前三项判断，不会必然降级为 `unknown`。

---

## 规则系统

ARK 内置 13 个规则文件。Claude Code 项目通过 `MEMORY.md` 引用；Codex 项目通过已安装插件中的 Skill 与项目 `AGENTS.md` 共同承载约定。

| 规则文件 | 作用 |
|----------|------|
| `ark.md` | 核心身份、原则、路由倾向、旧项目升级、Definition of Done |
| `artifact-roles.md` | Artifact 职责、Design vs Decide 边界、可信度四态 |
| `artifact-update-policy.md` | Artifact 回写条件和禁止性约束 |
| `capability-policy.md` | 依赖能力和降级策略 |
| `project-reality-policy.md` | 项目画像、真实性锚点、数据源元信息和验证保真度 |
| `extension-doc-policy.md` | 扩展文档类型、写入边界和漂移处理 |
| `artifact-placeholder-policy.md` | Artifact 模板占位与实质性内容判定 |
| `sub-agent-protocol.md` | sub-agent 写权限、输出格式和复核流程 |
| `external-review-gate.md` | 跨智能体外部审查门禁、风险分层、小批量审查和复检边界 |
| `task-sizing-summary.md` | 任务规模快速判断 |
| `task-sizing-rules.md` | 任务规模完整规则 |
| `python-backend-conventions.md` | Python 后端编码、fastchain-enhanced 中文注释和维护性规范 |
| `user-preferences.md` | 默认 Python 版本、工具和用户偏好 |

项目 `MEMORY.md` / `AGENTS.md` 由用户维护，不自动覆盖；插件中的规则文件会随插件更新生效。

---

## FAQ

### ARK 会替我自动执行完整流程吗？

不会。ARK 有自动路由倾向，但不会把一个 Skill 自动串到下一个 Skill。以 Artifact 为主要产出的 Skill 完成后会停止，并只建议下一步。

### Mode B 会改我的业务代码吗？

不会。Mode B 遵循 Inspect & Respect，不修改已有业务代码或项目配置；详细边界见上面的 Mode B 说明。

### Mode B 会安装 ruff 或 pyright 吗？

只有用户确认后才会安装。即使安装了工具，Mode B 也不会自动往 `pyproject.toml` 注入 ruff 配置。

### `ark-test` 和 `ark-validate` 有什么区别？

`ark-test` 可以创建或修改测试文件，并执行测试。`ark-validate` 只记录验证事实和证据，不修改源码，也不修复失败。

### `ark-review` 和 `ark-review-gate` 有什么区别？

`ark-review` 是 Claude Code 内部深度契约代码审查。`ark-review-gate` 是跨智能体外部审查门禁，用来决定当前 task 是否需要立即去 Codex/其他 agent 审查，还是可以进入同闭环低风险 batch；它还负责生成外部审查包、导入 findings、生成定向复检包。外部 review 通过后，仍需要 `ark-validate` 记录证据并推进 Done。

### `ark-solution` 和 `ark-design` 有什么区别？

`ark-design` 写 `docs/ark/design.md`，负责全局设计摘要、模块边界和扩展文档索引。`ark-solution` 写项目自有扩展文档，例如 `docs/solution/`、`docs/contracts/`、`docs/data-sources/`，负责专题详细方案、契约、集成和数据源元信息。

### ARK 会管理 data 目录吗？

不会。数据由项目自己管理，可以是本地目录、对象存储、外部系统或测试夹具。ARK 只记录数据源元信息、脱敏状态、样例范围和验证证据，不托管数据内容。

### Artifact 文件是否应该提交到 Git？

通常应该提交。ARK 的核心价值就是让项目状态随代码演进，被版本控制记录下来。

这条建议指 `docs/ark/*`、`CLAUDE.md`、`MEMORY.md`、`AGENTS.md` 等项目状态和规则入口；`.claude/` 是本地辅助配置，默认不提交。

### Codex 的 `AGENTS.md` 会写入本机插件路径吗？

不会。`AGENTS.md` 只记录项目级 ARK 约定、Artifact 位置和 Codex 中的自然语言触发方式，不写入某台机器的插件安装绝对路径。跨机器恢复时，应先在当前 Codex 环境安装 ARK 插件，再由 `AGENTS.md` 约束项目工作方式。

### ARK 和 superpowers / GSD 有什么区别？

ARK 的核心是项目内 Artifact 状态治理，强调 `docs/ark/` 文件、验证证据和中断恢复。superpowers 更偏通用技能触发和执行策略，GSD 更偏 coordinator/sub-agent 式任务分解。它们可以共存，但多插件环境中建议明确写“按 ARK 工作流...”来避免路由歧义。

### ARK 支持非 Python 项目吗？

Artifact 工作流本身可以用于其他语言和项目类型；当前初始化、质量工具和编码规范仍主要针对 Python 工程。项目画像用于区分后端服务、库/SDK、CLI、数据/AI、插件等不同真实性锚点。

---

## License

MIT License © 2026 Yingshufeng. See [LICENSE](LICENSE) for details.
