<div align="center">

# ARK

**Artifact-driven Reactive Kernel**

[![Version](https://img.shields.io/badge/version-1.0.4-blue.svg)](https://github.com/yingsf/ark)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-green.svg)](https://code.claude.com/docs/en/setup)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-purple.svg)](https://docs.anthropic.com/en/docs/claude-code/plugins)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

一套以个人开发体验为优先的 Claude Code 工作流内核，为 Python 后端项目提供 Artifact 驱动的任务管理、状态追踪与验证闭环。

[快速开始](#快速开始) · [安装](#安装) · [使用](#使用) · [指令辨析](#指令辨析) · [FAQ](#常见问题)

</div>

---

## 特性

- **Artifact 驱动** — 7 个核心产物构成项目状态面，跨会话可恢复
- **19 个专责 Skill** — 实现不验证、验证不修复、分析不执行，职责边界清晰
- **渐进式流程** — 小任务轻流程，大任务走完整流程，支持升降级
- **中断恢复** — 文件即状态，不受上下文窗口限制
- **批次实施** — 大改动自动拆批，每个批次是天然的中断安全点
- **Python 后端优先** — 内置 ruff / pyright hook，src layout 脚手架

---

## 快速开始

```bash
# 在 Claude Code 中执行

# 1. 添加 ark marketplace
/plugin marketplace add yingsf/ark

# 2. 安装插件
/plugin install ark@ark

# 3. 重新加载
/reload-plugins
```

进入你的项目目录：

```
/ark:ark-init       # 初始化 ARK 工作流
/ark:ark-helper     # 根据场景获得流程指引
```

详细安装选项和说明见下方 [安装](#安装) 章节。

---

## ARK 是什么

ARK 是一个 Claude Code 插件，为 Python 后端项目提供一套 Artifact 驱动的工程工作流，并内置 19 个可直接调用的 Skill。

传统 AI 编程的痛点：长任务中断后上下文丢失、实现完不知道验没验证、文档和代码逐渐失真、模糊需求被猜测执行。ARK 的解法不是加更多 prompt，而是建立一套 **Artifact（产物）驱动的状态系统**——把任务目标、设计方案、执行计划、验证证据全部写入项目文件，让每次会话都能从上次中断处精确恢复。

### 核心设计

**文件即状态** — 7 个核心 Artifact 构成项目的状态面，每个回答一个关键问题：

| Artifact | 回答的问题 |
|----------|-----------|
| `docs/ark/spec.md` | 要做什么 |
| `docs/ark/design.md` | 准备怎么做 |
| `docs/ark/plan.md` | 将如何分阶段推进 |
| `docs/ark/tasks.md` | 当前有哪些任务，各自什么状态 |
| `docs/ark/decisions.md` | 关键选择是什么，为什么这么选 |
| `docs/ark/validation.md` | 验证了什么，证据是什么 |
| `docs/ark/handoff.md` | 下次从哪里继续 |

**一个 Skill 一个职责** — 19 个 Skill 各司其职，实现不验证、验证不修复、分析不执行。每完成一步建议下一步，但绝不自动串联。

**渐进式适配** — 小任务走轻流程，大任务走完整流程。规模判断错误时支持升降级，而不是硬撑或降级处理。

### 19 个 Skill 一览

| 分类 | Skill | 职责 |
|------|-------|------|
| **启动** | `/ark:ark-init` | 初始化项目结构和工作流文件 |
| **澄清** | `/ark:ark-intake` | 澄清任务目标、范围、规模和推荐流程 |
| | `/ark:ark-helper` | 根据场景推荐最合适的 ARK 流程路径 |
| **分析** | `/ark:ark-analyze` | 扫描代码库，理解架构，可选预填充 spec/design |
| **规划** | `/ark:ark-spec` | 将需求结构化为规格文档 |
| | `/ark:ark-design` | 编写技术设计文档 |
| | `/ark:ark-plan` | 制定可恢复的执行计划 |
| | `/ark:ark-tasks` | 拆分可追踪的任务列表 |
| | `/ark:ark-decide` | 记录重要工程决策及理由 |
| **实施** | `/ark:ark-implement` | 最小可行实现，大改动自动拆批 |
| | `/ark:ark-debug` | 定位 bug 根因并制定低风险修复方案 |
| | `/ark:ark-refactor` | 在保持外部行为不变的前提下改善代码结构 |
| | `/ark:ark-review` | 审查代码变更的正确性和风险 |
| **验证** | `/ark:ark-test` | 创建和组织测试 |
| | `/ark:ark-validate` | 验证并记录验证证据（只验证不修复） |
| **恢复** | `/ark:ark-handoff` | 生成交接文档，为下次会话提供恢复点 |
| | `/ark:ark-next` | 根据当前状态裁决下一步 |
| | `/ark:ark-sync` | 同步代码现实与 Artifact 状态 |
| **文档** | `/ark:ark-docs` | 更新项目文档使其匹配真实实现 |

---

## 安装

### 前置要求

| 工具 | 用途 | 说明 |
|------|------|------|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | AI 编程助手 | CLI 或桌面端均可 |
| [Git](https://git-scm.com/) | 版本控制 | |
| Python 3.10+ | 运行时 | |

> 在全新 Python 项目场景下，`/ark:ark-init` 会按推荐配置为项目接入 [uv](https://docs.astral.sh/uv/)、[ruff](https://docs.astral.sh/ruff/)、[pyright](https://github.com/RobertCraigie/pyright-python) 和 [pytest](https://docs.pytest.org/)。已有项目模式下，这些工具仅在缺失时建议安装，不会自动注入配置。

### 安装插件

```bash
# 在 Claude Code 中执行以下 3 步

# 1. 添加 ark marketplace
/plugin marketplace add yingsf/ark

# 2. 安装 ark 插件（会提示选择安装范围，见下方说明）
/plugin install ark@ark

# 3. 重新加载插件
/reload-plugins
```

**安装范围说明：**

安装时会提示选择范围，大多数情况下选第一项即可：

| 选项 | 含义 | 适合谁 |
|------|------|--------|
| **Install for you** (user scope) | 安装到用户目录，所有项目可用 | 大多数用户，推荐 |
| **Install for this project** (project scope) | 写入项目配置，协作者共享 | 团队协作，需要所有人使用 ark |
| **Install locally** (local scope) | 仅当前仓库、仅当前用户生效 | 想先试用，不影响其他项目 |

### 在项目中初始化

安装插件后，在你的项目目录中执行：

```
/ark:ark-init
```

`/ark:ark-init` 提供两种模式：
- **模式 A（全新项目）**：从零创建完整的项目骨架 + ARK 工作流
- **模式 B（已有项目）**：只注入 ARK 工作流文件，不触碰已有代码

若启用了 ARK 提供的 hook 配置，编辑 Python 文件后可自动执行 `ruff format` 与 `ruff check --fix`。

### 升级

```bash
# 更新 marketplace 中的插件到最新版本
/plugin marketplace update ark
/reload-plugins
```

升级插件本身不会直接改动现有项目文件。若新版本引入了新的模板或工作流文件，建议在项目中重新运行 `/ark:ark-init`，并按提示选择是否更新相关文件。

### 卸载

```bash
# 移除 ark 插件
/plugin remove ark

# 如果不再需要 marketplace
/plugin marketplace remove ark
```

卸载不会删除你项目中的 `docs/`、`CLAUDE.md`、`MEMORY.md` 等 ARK 生成的文件。如需清理，手动删除即可。

---

## 使用

### 快速入口：不确定该用什么？

```
/ark:ark-helper
```

`/ark:ark-helper` 根据你的场景推荐最合适的流程路径。它不执行任何操作，只做导航。

### 场景 1：启动新项目

```
/ark:ark-init          → 初始化项目结构
/ark:ark-intake        → 澄清你想做什么（需求已明确可跳过）
/ark:ark-spec          → 将需求写成正式规格文档
/ark:ark-design        → 编写技术设计
/ark:ark-plan          → 制定阶段级执行计划
/ark:ark-tasks         → 拆分为可追踪任务
/ark:ark-implement     → 开始实现
/ark:ark-test          → 编写测试
/ark:ark-validate      → 记录验证结果
```

### 场景 2：接手已有项目

```
/ark:ark-init          → 模式 B：植入工作流（不碰代码）
/ark:ark-analyze       → 扫描理解代码库
# analyze 会预填充 spec/design，标注为"待确认"
/ark:ark-spec          → 审查确认需求
/ark:ark-design        → 审查确认设计
/ark:ark-plan          → 制定推进计划
/ark:ark-implement     → 开始实现
```

### 场景 3：收到一个模糊的需求

```
/ark:ark-intake        → 自动评估输入模糊度
                     Low  → 直接给出分析和推荐流程
                     Medium → 封闭式提问帮你澄清
                     High → 给示例帮你表达
# 澄清后，intake 会推荐下一步（可能是 spec、plan 或直接 implement）
```

### 场景 4：修一个 bug

```
/ark:ark-debug         → 定位根因，制定修复方案
/ark:ark-implement     → 实现修复
/ark:ark-test          → 补回归测试
/ark:ark-validate      → 记录验证证据
```

### 场景 5：上次中断了，今天继续

```
/ark:ark-next          → 自动裁决下一步
                     读取 handoff → tasks → plan → validation
                     告诉你最该做什么

# 如果文档可能过期（隔了很久）：
/ark:ark-sync          → 先同步代码与文档状态
/ark:ark-next          → 再裁决下一步

# 如果要保存当前进度并结束：
/ark:ark-handoff       → 记录恢复点
```

### 场景 6：实现完了要合并

```
/ark:ark-review        → 审查变更的正确性、风险和测试覆盖
/ark:ark-test          → 补充缺失的测试（如有）
/ark:ark-validate      → 记录验证闭环
```

### 工作流全景图

> 下图展示的是推荐路径，不是强制的线性流程。你可以根据任务规模跳过不需要的环节。

```
                    ┌──────────┐
          ┌────────►│ark-helper│◄── 不确定用什么？
          │         └──────────┘
          │
          ▼
     ┌──────────┐     ┌────────────┐     ┌────────────┐
     │ark-intake├────►│  ark-spec  ├────►│ ark-design │
     └──────────┘     └────────────┘     └────────────┘
          │                                    │
          │ （需求已明确时可跳过）                  │
          ▼                                    ▼
   ┌────────────┐                       ┌───────────┐
   │  ark-plan  ├──────────────────────►│ ark-tasks │
   └────────────┘                       └───────────┘
                                               │
       ┌───────────────────────────────────────┘
       ▼
┌──────────────┐     ┌──────────┐     ┌──────────────┐
│ark-implement ├────►│ ark-test ├────►│ ark-validate │
│ ark-debug    │     └──────────┘     └──────────────┘
│ ark-refactor │                            │
└──────────────┘                            │
       ▲                                    │
       │              ┌──────────────┐      │
       │              │ ark-handoff  │◄─────┘
       │              └──────────────┘
       │                     │
       └── ark-next ◄───────┘
            ark-sync
```

---

## 指令辨析

ARK 的 19 个 Skill 各有明确职责边界，但有些指令从名字上看容易混淆。以下逐一辨析。

### `/ark:ark-intake` vs `/ark:ark-spec` — "聊需求用哪个？"

| | `/ark:ark-intake` | `/ark:ark-spec` |
|---|---|---|
| **做什么** | 澄清任务：搞清楚你想做什么、有多大、该走什么流程 | 规格化：把澄清后的需求写成正式的规格文档 |
| **输入** | 原始用户请求（可能模糊） | 已澄清的需求、领域上下文、验收期望 |
| **输出** | 任务理解、规模判断、约束、假设、推荐流程路径 | `docs/ark/spec.md`：目标、范围、非目标、验收标准 |
| **写 Artifact 吗** | 不写任何 Artifact | 只写 `spec.md` |
| **典型时机** | 收到一个请求，还不太清楚要做什么 | 需求已清楚，要正式写成文档 |

**关系**：`intake` 是"搞清楚要做什么"，`spec` 是"把需求正式写成规格"。它们是上下游，不是替代关系。

```
"我想加个用户认证"  →  /ark:ark-intake（澄清范围）  →  /ark:ark-spec（写规格）
"需求我清楚了"      →  直接 /ark:ark-spec（跳过 intake）
"这个太慢了"        →  /ark:ark-intake（High fuzziness，帮你表达需求）
```

### `/ark:ark-plan` vs `/ark:ark-tasks` — "规划工作用哪个？"

| | `/ark:ark-plan` | `/ark:ark-tasks` |
|---|---|---|
| **做什么** | 制定阶段级执行策略 | 拆分为可追踪的粒度任务 |
| **产出** | `docs/ark/plan.md`：阶段划分、里程碑、风险、验证策略 | `docs/ark/tasks.md`：任务列表 + 状态（Todo/Doing/Done/Blocked） |
| **粒度** | 阶段级——"先做 A，再做 B，B 完成后验证" | 任务级——"任务 1：创建用户模型（Todo，高优先级）" |
| **回答的问题** | "分几个阶段？每个阶段的入口/出口是什么？" | "当前有哪些具体任务？各自什么状态？" |

**关系**：`plan` 先出阶段策略，`tasks` 再把阶段拆成可追踪任务。`plan` 的建议下一步就是 `/ark:ark-tasks`。

```
/ark:ark-plan  →  "分 3 个阶段：数据层 → API 层 → 集成测试"
/ark:ark-tasks  →  "阶段 1 拆为：T1 创建模型(Doing) T2 写迁移(Todo) T3 补测试(Todo)"
```

### `/ark:ark-test` vs `/ark:ark-validate` — "验证代码用哪个？"

| | `/ark:ark-test` | `/ark:ark-validate` |
|---|---|---|
| **做什么** | 写测试代码并执行 | 记录"验证了什么、证据是什么" |
| **改代码吗** | **是** — 创建/修改测试文件 | **绝不** — 纯记录，连一行 import 都不改 |
| **产出** | 测试文件 + 执行结果摘要 | `docs/ark/validation.md`：已验证项、未覆盖项、风险结论 |
| **回答的问题** | "测试怎么写？跑出来的结果是什么？" | "当前验证了什么？还有什么没验证？验证强度够不够？" |

**关系**：`test` 产生测试代码和执行结果，`validate` 把这些结果（连同其他验证手段）记录为正式证据。`test` 的输出是 `validate` 的输入。

```
/ark:ark-test     →  写了 5 个测试，跑出 4 passed 1 failed
/ark:ark-validate  →  记录：已验证 X（测试通过），未验证 Y（需要真实环境），风险 Z
```

### `/ark:ark-analyze` vs `/ark:ark-review` — "看代码用哪个？"

| | `/ark:ark-analyze` | `/ark:ark-review` |
|---|---|---|
| **做什么** | 理解整个代码库的架构和模块关系 | 评审具体代码变更的质量 |
| **范围** | 全局 — 整个项目 | 局部 — 具体的改动文件 |
| **适用时机** | 第一次接触项目、重构前重新理解 | 实现完成后、合并前 |
| **产出** | 项目概览、模块地图、数据流、可选预填充 spec/design | 问题清单（Critical/Major/Minor）、风险点、合并建议 |

**关系**：`analyze` 是"认识这个项目"，`review` 是"这批改得好不好"。前者面向全局认知，后者面向局部质量。

```
接手陌生项目  →  /ark:ark-analyze（建立全局认知）
实现完一个功能  →  /ark:ark-review（检查改动质量）
```

### `/ark:ark-sync` vs `/ark:ark-next` — "中断后恢复用哪个？"

| | `/ark:ark-sync` | `/ark:ark-next` |
|---|---|---|
| **做什么** | 修文档失真 — 让 Artifact 重新匹配代码现实 | 裁决下一步 — 告诉你现在最该做什么 |
| **条件判断** | 文档是否过期、状态是否冲突 | 哪个环节未闭合、什么是最高优先级 |
| **会改文件吗** | 会 — 可修正状态字段（不改变语义内容） | 不会 — 只读 Artifact，输出建议 |
| **产出** | 一致性评估 + 建议更新的 Artifact 列表 | 当前阶段 + 最重要未完成项 + 推荐的下一个 Skill |

**关系**：如果你怀疑文档过期了，先 `/ark:ark-sync` 修状态，再 `/ark:ark-next` 看该做什么。如果文档状态可信，直接 `/ark:ark-next` 即可。

```
隔了 3 天回来，不确定文档是否过期  →  /ark:ark-sync → /ark:ark-next
刚中断 10 分钟，文档应该还准    →  直接 /ark:ark-next
```

---

## 10 个让 ARK 与众不同的机制

### 1. 增量锚定分析 (`/ark:ark-analyze`)

4 阶段写入工作文档，每阶段从文件读取而非依赖上下文记忆，防止 AI 幻觉。分析结果区分 `[fact]`（事实）、`[inferred]`（推断）、`[uncertain]`（不确定）三级可信度，所有推断必须标注依据。

### 2. 3 级模糊度分流 (`/ark:ark-intake`)

用户输入不一定清晰。ARK 根据信号自动分级：
- **Low**（目标明确）→ 直接输出分析结果
- **Medium**（有方向但模糊）→ 封闭式提问，每题给 2-3 个选项，最多 3 题
- **High**（只有感受/否定）→ 示例驱动启发，提供常见场景的专业表达作为脚手架

### 3. 批次实施机制 (`/ark:ark-implement`)

改动涉及 3+ 文件时自动触发批次拆分。每个批次定义 4 要素：目标、涉及文件、修改锚点、完成信号。批次完成点就是天然的中断安全点——所有文件修改已落盘、局部检查已执行。即使会话中断，下次也能从上一个完成批次继续。

### 4. 只验证不修复 (`/ark:ark-validate`)

验证和修复是两件不同的事。`/ark:ark-validate` 的硬边界是：**只记录验证状态，绝不修改代码**。即使发现只差一行 import，也必须交给 `/ark:ark-debug` 处理。mock 环境的验证结果永远不报告为"通过"。

### 5. 裁决优先级序列 (`/ark:ark-next`)

中断恢复不是拍脑袋。`/ark:ark-next` 按确定性决策链裁决：状态可信性 → 验证闭环 → 活跃执行项 → 回退规划层。依次读取 handoff → tasks → plan → validation → spec/design，找到第一个未闭合的环节。

### 6. Inspect & Respect (`/ark:ark-init` Mode B)

在已有项目上启用 ARK 时，只检测不修改。不触碰 `pyproject.toml`、代码目录、`.gitignore` 等任何已有文件。质量工具（ruff、pyright）只报告检测结果和建议，绝不自动注入配置。

### 7. 变量探测规则

模板生成从不硬编码。Python 版本从 `pyproject.toml` 的 `requires-python` 探测，源码目录从实际目录结构探测，测试目录检查 `tests/`/`test/` 是否存在。探测失败时诚实退化并标注默认值。

### 8. 渐进式任务规模适配

Small / Medium / Large 三档，每档有明确的特征、推荐流程和最低 Artifact 要求。出现升级信号（跨文件、跨会话、架构影响）时自动升级。默认按 Medium 处理——宁可轻微过度规划，不可草率执行。

### 9. 文件即状态的跨会话恢复

不受上下文窗口限制。`/ark:ark-handoff` 记录完成/未完成/风险/关键文件，`/ark:ark-next` 读取所有 Artifact 裁决恢复路径。即使隔了三天、换了设备，只要文件在，状态就在。

### 10. 预填充与审查确认分离

`/ark:ark-analyze` 可以从代码反推并预填充 `spec.md` 和 `design.md`，但会标注为 `<!-- 由 /ark:ark-analyze 自动生成，需人工确认 -->`。后续必须经过 `/ark:ark-spec` 或 `/ark:ark-design` 审查确认，不能直接当作已确认的需求或设计使用。

---

## 项目结构

安装 ARK 插件并执行 `/ark:ark-init` 后，你的项目会获得以下结构（以全新项目为例）：

```
my_project/
├── docs/                        # 项目文档
│   └── ark/                     # ARK Artifact 目录
│       ├── spec.md              # 需求规格
│       ├── design.md            # 技术设计
│       ├── plan.md              # 执行计划
│       ├── tasks.md             # 任务列表
│       ├── decisions.md         # 决策记录
│       ├── validation.md        # 验证记录
│       └── handoff.md           # 交接文档
├── src/my_project/              # 源代码（src layout）
│   └── __init__.py
├── tests/                       # 测试
│   ├── __init__.py
│   └── conftest.py
├── pyproject.toml
├── CLAUDE.md                    # Claude Code 项目上下文
├── MEMORY.md                    # ARK 规则入口
└── .claude/settings.local.json  # ARK hook 与权限配置
```

---

## 规则系统

ARK 内置 7 个规则文件，通过 MEMORY.md 加载：

| 规则文件 | 内容 |
|----------|------|
| `ark.md` | 核心身份、原则、强制行为约束 |
| `artifact-roles.md` | 每个 Artifact 的职责边界 |
| `artifact-update-policy.md` | Artifact 回写条件和禁止性约束 |
| `task-sizing-rules.md` | 任务规模完整判定规则 |
| `task-sizing-summary.md` | 任务规模快速判断表 |
| `python-backend-conventions.md` | Python 后端编码规范 |
| `user-preferences.md` | 用户偏好默认值 |

---

## 常见问题

### ARK 适合什么人？

适合使用 Claude Code 进行 Python 后端开发的个人开发者和小团队。特别是经常处理跨会话的中大型任务、需要清晰的任务追踪和验证记录的场景。

### ARK 和手写 CLAUDE.md + skills 有什么区别？

手写 CLAUDE.md 和 skills 是一次性的静态指令，没有跨会话的状态管理。ARK 的核心差异是：

- **Artifact 是活的** — 随实现推进持续更新，不是写完就固定的文档
- **Skill 之间有协作约束** — 实现不验证、验证不修复，强制分离关注点
- **中断恢复是内置的** — handoff → next 的裁决链让你从任何断点恢复
- **任务规模自适应** — 自动判断该走轻流程还是完整流程

### ARK 支持其他语言吗？

当前专注于 Python 后端。规则中的编码规范和项目脚手架是 Python 特有的，但 Artifact 工作流本身（spec、plan、tasks、validation 等）是语言无关的。

### 已有项目可以用吗？

可以。`/ark:ark-init` 的模式 B 专为已有项目设计，只注入工作流文件，不修改任何已有代码和配置。

### 我必须走完整流程吗？

不是。小任务可以跳过 spec/design/plan，直接从 intake → implement → validate。ARK 的设计是**渐进式**的——任务越复杂，用到的 Artifact 越多。

### Artifact 文件会污染我的仓库吗？

初始生成的 Artifact 文件保持轻量，均为纯文本，适合直接纳入 Git 管理并随项目演进持续维护。`/ark:ark-sync` 可以检测并清理过期内容。

---

## 许可证

MIT License © 2026 Yingshufeng. See [LICENSE](LICENSE) for details.
