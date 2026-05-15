---
name: ark-solution
description: |
  编写或更新核心 Artifact 之外的专题方案、详细设计、契约、集成或数据源元信息文档。
  触发时机：spec/design 已给出边界，但实现前仍需要详细方案、接口契约、数据源说明或专题设计时。
  关键词：solution、详细方案、专题设计、详细设计、contracts、契约、接口文档、数据源、集成方案。
version: "1.0"
---

# /ark-solution

## 目标

在不污染 `docs/ark/` 7 个核心 Artifact 的前提下，生成或维护项目自有的扩展文档：专题方案、详细设计、接口契约、集成方案、数据源元信息、运维手册、迁移方案、安全说明、调研记录或示例文档。

## 适用场景

- spec 已明确"要做什么"，但某个专题还需要详细方案才能进入 plan/tasks
- design 已明确全局架构，但某个模块、接口、集成或数据链路需要更细粒度设计
- 需要写 HTTP/MCP/API/CLI/SDK/文件格式/事件契约
- 需要记录外部系统接入、数据源元信息、运行手册、迁移步骤或安全边界
- implement/debug/refactor/sync 识别到扩展文档漂移，需要更新专题文档

## 不适用场景

- 需求范围、能力承诺或验收标准仍不清楚（先 `/ark:ark-spec` 或 `/ark:ark-intake`）
- 缺的是全局技术设计摘要（用 `/ark:ark-design`）
- 缺的是阶段计划或任务状态（用 `/ark:ark-plan` / `/ark:ark-tasks`）
- 缺的是 README、安装说明、用户使用文档（通常用 `/ark:ark-docs`）
- 用户只是想立刻编码（用 `/ark:ark-implement`）

## 输入

- 用户指定的专题、目标和文档类型
- `docs/ark/spec.md` 与 `docs/ark/design.md`（如存在）
- 当前代码、配置、接口、数据源元信息或外部系统约束
- 相关扩展文档（如已有）

## 输出

- 新增或更新的扩展文档
- 与 `spec.md` / `design.md` / `decisions.md` 的关系说明
- 若核心 Artifact 需要同步，输出建议的后续 Skill

## 相关规则

- 扩展文档规则见 `${CLAUDE_PLUGIN_ROOT}/rules/extension-doc-policy.md`
- 项目真实性规则见 `${CLAUDE_PLUGIN_ROOT}/rules/project-reality-policy.md`

## 可写范围

可按需创建或更新：
- `docs/solution/*`
- `docs/design/*`
- `docs/contracts/*`
- `docs/integrations/*`
- `docs/data-sources/*`
- `docs/operations/*`
- `docs/runbooks/*`
- `docs/migration/*`
- `docs/security/*`
- `docs/research/*`
- `docs/examples/*`

不得直接写入任何 `docs/ark/*` 核心 Artifact。若需要更新核心 Artifact，只能在输出中建议对应 Skill。

## 文档类型选择

| 用户目标 | 推荐类型 |
|----------|----------|
| 功能或阶段的详细解决方案 | `docs/solution/<topic>.md` |
| 模块、组件、子系统内部设计 | `docs/design/<topic>.md` |
| HTTP/MCP/API/CLI/SDK/文件格式/事件契约 | `docs/contracts/<topic>.md` |
| 外部系统接入方式、配置、认证、失败语义 | `docs/integrations/<topic>.md` |
| 数据来源、样例范围、脱敏状态、访问方式 | `docs/data-sources/<topic>.md` |
| 启动、部署、排障、运行操作 | `docs/operations/<topic>.md` 或 `docs/runbooks/<topic>.md` |
| 迁移、升级、兼容性路径 | `docs/migration/<topic>.md` |
| 权限、安全边界、密钥、审计、威胁模型 | `docs/security/<topic>.md` |
| Spike、调研、备选技术比较 | `docs/research/<topic>.md` |
| 可执行示例或典型输入输出 | `docs/examples/<topic>.md` |

## 工作流

1. 明确本次要写的专题、文档类型、受众和使用时机。
2. 读取相关核心 Artifact 和现有扩展文档，确认边界是否足够稳定。
3. 若发现需求范围或验收标准不清，停止并建议 `/ark:ark-spec`；不得用 solution 代替 spec。
4. 若只是全局架构摘要缺失，建议 `/ark:ark-design`；不得用专题文档取代 design。
5. 选择目标目录和文件名。文件名应语义化，使用 kebab-case 或项目既有命名风格。
6. 只写与专题直接相关的内容，避免把 plan/tasks/validation 混入专题文档。
7. 对涉及真实依赖或数据的文档，按项目真实性规则记录真实性锚点、数据源元信息、替身边界和验证建议。
8. 写入扩展文档，建议包含轻量头部：
   ```markdown
   <!-- ark-extension-doc: <type> -->
   <!-- ark-related-artifacts: docs/ark/spec.md, docs/ark/design.md -->
   <!-- ark-status: draft / active / stale / superseded -->
   ```
9. 完成后检查是否需要后续同步：
   - 全局设计索引需要更新 → 建议 `/ark:ark-design`
   - 核心范围或验收变化 → 建议 `/ark:ark-spec`
   - 关键取舍需要记录 → 建议 `/ark:ark-decide`
   - 可以进入执行计划 → 建议 `/ark:ark-plan`

## 数据源文档特别规则

- 只记录数据源元信息，不复制数据内容。
- 可记录本地路径、对象存储位置、格式、样例规模、脱敏状态、访问权限、验证时使用的样本范围。
- 不记录密钥、连接串、账号密码、敏感原文或大体量数据片段。
- 若数据不提交 git，应明确写"项目本地/外部管理，ARK 不托管数据内容"。
- 大文件、大目录、压缩包、FTP/对象存储路径必须先记录路径、类型、大小、数量和样例范围；再按 header、少量样例或代表性片段抽样，不得全文复制。
- 数据源结论必须标注采样覆盖范围与未覆盖风险；不得把抽样观察描述为全量验证结论。

## 验证要求

- 扩展文档必须能说明它支撑哪个 spec/design/plan 主题。
- 不得把探索性 `research` 文档写成已确认设计。
- 不得把 mock/fake/合成数据方案描述为真实依赖已接入。
- 若实现已经存在，文档必须基于真实代码和配置，不得编造不存在的接口或目录。
- 不得修改任何 `docs/ark/*` 核心 Artifact。

## 停止条件

- 扩展文档已足以支撑后续 design 索引、plan 拆解或 implement 执行
- 或已明确指出边界不足，需要先回到 spec/design/intake

## 固定输出格式

### 1. 文档类型与目标
- 类型：
- 目标专题：
- 写入路径：

### 2. 主要内容摘要
- 关键方案：
- 契约/接口：
- 真实依赖或数据源：
- 替身边界：

### 3. 与核心 Artifact 的关系
- `spec.md`：一致 / 建议更新（原因）
- `design.md`：一致 / 建议更新索引或摘要（原因）
- `decisions.md`：无需更新 / 建议 `/ark:ark-decide`

### 4. 建议下一步
- 若需要更新全局设计索引 → `/ark:ark-design`
- 若可以拆解执行 → `/ark:ark-plan`
- 若可直接实施 → `/ark:ark-implement`

## 备注

`/ark:ark-solution` 是核心 Artifact 之外的专题承载层。它让详细设计有地方放，但不改变 ARK 的 7 个核心 Artifact 设计。
