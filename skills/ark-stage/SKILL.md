---
name: ark-stage
description: |
  治理多 MVP / 多阶段项目的阶段状态、阶段收口、归档、继承提炼和新阶段初始化。
  触发时机：阶段结束、进入新 MVP、阶段状态冲突、需要归档当前 7 个 Artifact、需要生成阶段摘要或 carryover gate。
  关键词：阶段、stage、MVP、归档、archive、阶段切换、进入下一阶段、收口、carryover gate。
version: "1.0"
---

# /ark-stage

## 目标

`ark-stage` 是 ARK 的阶段治理 Skill。它用于大项目、多 MVP、多阶段交付中的阶段切换，负责判断当前阶段真实状态、收口和归档当前阶段、生成阶段摘要、维护阶段索引、提炼可继承结论、初始化新阶段当前态，并管理跨阶段 carryover gate。

本 Skill 不实现代码、不修复 bug、不执行测试、不替代 `/ark:ark-validate`，也不得把旧阶段验证自动当成新阶段通过。

## 适用场景

- 当前 MVP / 阶段准备收口
- 用户要从 S1 进入 S2、从 MVP-1 进入 MVP-2、从 Alpha 进入 Beta
- `tasks.md`、`validation.md`、`handoff.md`、`plan.md` 对阶段状态判断不一致
- 需要将当前 7 个核心 Artifact 归档到 `docs/ark/archive/<stage-id>/`
- 需要生成 `stage-summary.md`
- 需要创建或更新 `docs/ark/stages.md`
- 需要把上一阶段未闭合项转为下一阶段 carryover gate

## 不适用场景

- 只是当前阶段内的普通同步：优先 `/ark:ark-sync`
- 只是继续当前任务：优先 `/ark:ark-next`
- 只是会话暂停和恢复点记录：优先 `/ark:ark-handoff`
- 只是记录实现验证：优先 `/ark:ark-validate`
- 用户只想修改业务代码或测试代码

## 模式

必须先判断用户意图对应的模式。除 `stage-status` 外，其他模式都必须先输出 preview 并等待用户确认，确认后才写文件。

| 模式 | 行为 | 写入 |
|---|---|---|
| `stage-status` | 只读审计当前阶段 | 不写文件 |
| `stage-close` | 收口当前阶段，生成 summary，归档当前 7 个 Artifact，更新 stages | 需 preview + 确认 |
| `stage-open` | 开启新阶段，从 archive 或当前状态提炼继承项，重建当前 7 个 Artifact，更新 stages | 需 preview + 确认 |
| `stage-transition` | `stage-close` + `stage-open`，一次完成阶段收口、归档、继承和新阶段初始化 | 需 preview + 确认 |

如果用户没有明确模式，先执行 `stage-status` 只读审计，并根据结果推荐可选模式。

## 阶段状态

必须输出阶段状态，并说明证据。

| 状态 | 含义 |
|---|---|
| `active` | 阶段仍在正常推进，有 Todo / Doing |
| `ready-to-close` | 无 Doing / Ready for validation，核心任务 Done，只有可接受尾项 |
| `blocked` | 存在阻塞项，且阻塞项影响阶段闭合 |
| `closed` | 阶段目标完成，Done 均有 validation 证据，无遮挡风险 |
| `closed-with-risk` | 用户确认带风险归档或进入下一阶段 |
| `conflicting` | `tasks`、`validation`、`handoff`、`plan` 存在明显冲突 |
| `unknown` | 缺关键 Artifact 或证据不足 |

判定优先级：

```text
conflicting > blocked > active > ready-to-close > closed
```

`blocked` / `conflicting` 只有在用户明确确认后，才可归档为 `closed-with-risk`。不得静默写成 `closed`。

## 读取范围

优先读取：

1. `docs/ark/spec.md`
2. `docs/ark/design.md`
3. `docs/ark/plan.md`
4. `docs/ark/tasks.md`
5. `docs/ark/decisions.md`
6. `docs/ark/validation.md`
7. `docs/ark/handoff.md`
8. `docs/ark/stages.md`（如存在）
9. `docs/ark/archive/`（如执行 open / transition 且需要读取历史阶段）
10. 当前文件现实和 `git status`（如可用，仅用于判断阶段状态，不写代码）

缺少 7 个核心 Artifact 时必须停止，并建议先执行 `/ark:ark-init` Mode B 或手动补齐 Artifact。

## 一致性审计

每次运行都必须先完成以下审计：

1. 7 个核心 Artifact 是否存在。
2. Artifact 是否有 `ark-artifact`、`schema-version`、`last-updated` 版本头。
3. `tasks.md` 状态分布：Done / Ready for validation / Doing / Todo / Blocked。
4. Done 任务是否都有 `validation.md` 证据引用。
5. Ready for validation 是否未闭合。
6. Blocked 是否存在，是否影响阶段闭合。
7. `validation.md` 是否包含阶段最终闭环证据。
8. `handoff.md` 是否滞后于 `tasks.md` / `validation.md`。
9. `plan.md` 当前状态是否滞后于 `tasks.md`。
10. `decisions.md` 中哪些是仍有效的项目级长期决策，哪些是阶段性决策，哪些已被替代。
11. 是否存在 bounded / fake / fixture 验证被夸大为真实交付闭环。
12. 是否存在敏感数据、大体量原文或连接串被写入 Artifact 的风险信号。

模板占位与实质性内容判定必须遵循 `${CLAUDE_PLUGIN_ROOT}/rules/artifact-placeholder-policy.md`。不得把阶段模板中的空字段、状态选项、表头、`YYYY-MM-DD` 或 `待填写` 当作真实阶段结论。

若存在明显冲突，应输出冲突矩阵，并说明推荐信任顺序。默认信任顺序：

```text
validation.md 真实验证证据 > tasks.md 当前状态 > handoff.md 恢复提示 > plan.md 当前状态
```

但不得在未确认的情况下直接覆盖冲突文件。

## 用户确认规则

以下情况必须阻塞确认：

- 存在 Blocked 且用户要 close / transition
- 存在 Ready for validation
- Done 缺 validation 证据
- `handoff.md` 与 `tasks.md` / `validation.md` 冲突
- `plan.md` 当前状态明显过期
- archive 目录已存在
- 用户要求覆盖当前 7 个 Artifact
- 新阶段 id / title 缺失
- 要将阶段状态写成 `closed-with-risk`

确认选项必须明确列出，建议：

```text
1. 停止，不写文件
2. 只归档为 blocked
3. 带风险归档为 closed-with-risk，并生成 carryover gates
4. 先执行 ark-sync / ark-validate 后再回来
```

如果当前运行环境没有可用的交互式提问机制，退化为普通文本提问并等待用户下一条消息，不得继续写文件。

## Preview 规则

除 `stage-status` 外，必须先输出 preview。preview 至少包含：

- 将写入哪些文件
- 将归档哪些文件
- 当前阶段判定状态
- 是否存在 blocked / conflicting / stale
- 新阶段将继承哪些内容
- `decisions.md` 中哪些决策继续保留、仅归档或标记为 superseded
- 哪些内容不会继承
- carryover gate 列表
- 风险确认项

用户确认后才能执行写入。确认前不得创建 archive、不得重建当前 7 个 Artifact、不得更新 `stages.md`。

## 归档结构

归档路径：

```text
docs/ark/archive/<stage-id>/
```

归档内容：

```text
docs/ark/archive/<stage-id>/
  spec.md
  design.md
  plan.md
  tasks.md
  decisions.md
  validation.md
  handoff.md
  stage-summary.md
```

归档规则：

- 7 个 Artifact 原样复制。
- 不清洗 archive 内容。
- 不修改 archive 内的历史文档。
- 不把 archive 当当前执行依据。
- archive 中的 `decisions.md` 是历史快照，不等同于新阶段当前有效决策。
- `stage-summary.md` 负责解释归档时可信度、冲突和风险。

`stage-summary.md` 优先使用 `${CLAUDE_PLUGIN_ROOT}/templates/stage/stage-summary.template.md`，模板不可用时使用本文「stage-summary.md 最小结构」。

## stages.md

`docs/ark/stages.md` 是阶段索引，不属于初始化默认 7 个核心 Artifact，仅在 `ark-stage` 需要时创建或更新。

优先使用 `${CLAUDE_PLUGIN_ROOT}/templates/stage/stages.template.md`，模板不可用时使用本文「stages.md 最小结构」。

`stages.md` 必须包含：

- Current Stage
- Stage History
- Carryover Gates
- Long-Lived Inheritance

## Carryover Gates

如果上一阶段有未闭合项，但用户确认进入下一阶段，必须写入 carryover gate。

示例：

```markdown
| T31 真实 .data 样例导入闭环 | S1 | S2 消息资产化分流验收前 | blocked | validation.md 缺 T31 |
```

规则：

- carryover gate 不是普通 Todo。
- gate 是下一阶段的前置约束或验收门禁。
- gate 必须保留来源阶段、要求完成时间点、当前状态和证据。
- gate 不能被静默删除。
- gate 未完成时，`ark-next` 应优先提醒。

## 新阶段当前 7 个 Artifact 处理

`stage-open` / `stage-transition` 会重建当前 7 个 Artifact，但不是清空，也不是全文继承。

| Artifact | 处理规则 |
|---|---|
| `spec.md` | 继承产品不变量、仍有效验收边界、上一阶段未闭合风险、新阶段目标 |
| `design.md` | 继承已落地架构、稳定接口、输入/输出约束、下一阶段不能破坏的设计 |
| `plan.md` | 重建为新阶段计划；旧阶段 plan 只进 archive |
| `tasks.md` | 清除旧 Done 堆积；只保留新阶段 Todo / Doing / Blocked 和 carryover gate |
| `decisions.md` | 保留所有仍有效的项目级长期决策；阶段性决策归档；不确定时默认保留；不得生成空的 `decisions.md` |
| `validation.md` | 保留验证基线摘要；详细历史验证归档 |
| `handoff.md` | 重写为新阶段恢复点 |
| `stages.md` | 更新 current stage、history、carryover gates 和 inheritance |

## 长期决策与阶段决策分类

`decisions.md` 是项目级长期记忆和当前仍有效决策索引，不是阶段局部任务记录。`ark-stage` 必须把它当作跨阶段资产处理。

硬规则：

- `stage-close` 只归档当前 `decisions.md` 的历史快照，不重写当前 `decisions.md`。
- `stage-open` / `stage-transition` 不得生成空的 `decisions.md`，除非审计证明没有任何仍有效的项目级决策，并在 preview / `stage-summary.md` 说明依据。
- 仍有效的项目级长期决策必须继续保留在当前 `decisions.md`。
- 不确定是否仍有效的决策，默认保留，不默认丢弃。
- 已被推翻或替代的长期决策不得静默删除；应在当前 `decisions.md` 中标记为 `superseded` / 已替代，并引用替代决策或替代依据。
- 阶段性决策只有在明确不再约束新阶段时，才可不写入新阶段当前 `decisions.md`；其历史仍必须留在 archive 快照中。
- 仍约束下一阶段但带有未解决风险的决策，必须保留，并同步写入 Carryover Gates 或 `stage-summary.md` 的未覆盖风险。

长期决策继续保留在当前 `decisions.md`：

- 技术选型
- 架构原则
- 命名规范
- 配置治理
- 真实验证策略
- 数据安全边界
- 不应反复讨论的取舍

阶段性决策进入 archive，不再污染当前阶段上下文：

- 某阶段临时实现路线
- 某阶段任务顺序
- 临时验证方案
- 已完成但不再影响当前阶段的选择

## 验证继承规则

旧阶段 `validation.md` 不能原样继承为新阶段「已通过」。

只允许继承为：

- 验证基线
- 历史证据
- 可复用检查项
- 未覆盖风险
- 下一阶段必须重新验证的门禁

禁止：

- 上一阶段通过 → 新阶段自动通过
- bounded validation → 真实交付闭环
- fixture/fake/mock → 真实数据验证

## 写权限

按模式限制：

| 模式 | 写权限 |
|---|---|
| `stage-status` | 无写权限 |
| `stage-close` | `docs/ark/archive/<stage-id>/*`、`docs/ark/stages.md`，必要时更新 `handoff.md` |
| `stage-open` | 当前 7 个 Artifact、`docs/ark/stages.md` |
| `stage-transition` | archive、stages、当前 7 个 Artifact |

禁止写：

- 源代码
- 测试代码
- 项目配置
- `.data/`
- 真实数据内容
- 密钥 / 连接串

## 停止条件

遇到以下情况必须停止：

- 缺少核心 Artifact。
- 无法判断当前阶段。
- 用户未提供 stage id / title。
- archive 目录已存在且未确认处理方式。
- 要带风险归档但用户未确认。
- 要重建当前 7 个 Artifact 但用户未确认 preview。
- 发现敏感数据风险，需要用户确认处理策略。
- 用户要求 `closed`，但证据只支持 `blocked` 或 `closed-with-risk`。

## stage-summary.md 最小结构

```markdown
<!-- ark-stage-summary: <stage-id> -->
<!-- schema-version: 1.0 -->
<!-- generated-at: YYYY-MM-DD -->

# Stage Summary: <stage-id> <stage-title>

## 1. 阶段结论

- 阶段状态：
- 阶段目标：
- 是否建议进入下一阶段：
- 主要原因：

## 2. 完成摘要

- 已完成能力：
- 已完成任务：
- 已形成工程资产：
- 已形成长期决策：

## 3. 未完成 / 阻塞

| 项 | 状态 | 原因 | 对下一阶段影响 |
|---|---|---|---|

## 4. 验证摘要

| 验证对象 | 保真度 | 真实性锚点 | 结论 | 未覆盖 |
|---|---|---|---|---|

## 5. 可继承结论

### 需求 / 不变量

### 设计约束

### 长期决策

- 继续保留到当前 `decisions.md`：
- 标记为 `superseded` / 已替代：
- 仅保留在 archive 的阶段性决策：
- 不确定但默认保留：

### 验证基线

### 未覆盖风险

## 6. 不应继承的内容

- 已完成历史任务
- 仅属于旧阶段的恢复提示
- 已过期 plan 当前状态
- 已失效 handoff
- 阶段性调试记录
- 不能证明新阶段通过的旧验证

## 7. 下一阶段建议

- 推荐下一阶段：
- 前置门禁：
- 推荐 Skill：
- 第一批任务建议：
```

## stages.md 最小结构

```markdown
<!-- ark-artifact: stages -->
<!-- schema-version: 1.0 -->
<!-- last-updated: YYYY-MM-DD -->

# ARK Stages

## Current Stage

- stage-id:
- title:
- status:
- started-at:
- source-stage:
- archive:
- primary-gate:
- risk-level:

## Stage History

| Stage | Title | Status | Archive | Summary | Key Risk |
|---|---|---|---|---|---|

## Carryover Gates

| Gate | Source Stage | Required Before | Status | Evidence |
|---|---|---|---|---|

## Long-Lived Inheritance

### Product / Requirement Invariants

### Design Constraints

### Decisions

### Validation Baselines

### Known Risks
```

## 固定输出格式

```markdown
## 阶段治理结果

### 1. 阶段信息

- 当前阶段：
- 操作模式：
- 判定状态：
- 归档路径：
- 新阶段：

### 2. 一致性审计

| 检查项 | 状态 | 证据 | 影响 |
|---|---|---|---|

### 3. 阶段结论

- 是否可 closed：
- 是否可进入下一阶段：
- 需要用户确认的风险：

### 4. Preview / 已执行写入

| 文件 | 动作 |
|---|---|

### 5. 继承项

- 需求 / 不变量：
- 设计约束：
- 长期决策：
- 验证基线：
- 未覆盖风险：

### 6. Carryover Gates

| Gate | Required Before | Status |
|---|---|---|

### 7. 下一步

- 推荐 Skill：
- 本轮唯一下一步：
```

## 与其他 Skill 的关系

| Skill | 职责 |
|---|---|
| `ark-sync` | 阶段内文档与现实同步 |
| `ark-next` | 当前阶段下一步裁决 |
| `ark-handoff` | 当前会话恢复点 |
| `ark-stage` | 阶段级收口、归档、继承和新阶段初始化 |

如果发现阶段内冲突严重，可以建议先执行 `/ark:ark-sync`。如果用户明确要求带风险归档，也可以继续，但必须写入 `closed-with-risk` 和 carryover gate。

## 示例裁决

若 `tasks.md` 显示 T39 Done、T31 Blocked，`validation.md` 有 T39 但无 T31，`handoff.md` 仍停在 T38，`plan.md` 仍写 not started，则应输出：

```text
阶段状态：conflicting / blocked
不建议直接 closed
可选：先执行 ark-sync 修正 handoff/plan；归档为 blocked；或用户确认 closed-with-risk 并将 T31 写入 carryover gate
```
