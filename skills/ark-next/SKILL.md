---
name: ark-next
description: |
  基于当前 Artifact 与仓库状态，判断最合理的下一步动作，尤其用于中断恢复与长任务续接。
  触发时机：需要恢复中断任务、切回长周期任务、不确定先做什么时。
  关键词：下一步、接下来做什么、恢复任务、续接、next、继续、从哪里开始。
version: "1.0"
---

# /ark-next

## 目标
基于当前 Artifact 与仓库状态，判断最合理的下一步动作，尤其用于中断恢复与长任务续接。

## 适用场景
- 需要恢复中断任务
- 切回一个长周期任务
- 当前状态存在多个可能方向，不确定先做什么

## 不适用场景
- 下一步动作已非常明确且正在执行
- 当前任务极小且无需状态恢复
- 项目没有足够文档或代码状态可供判断

## 输入
- 当前仓库状态、`docs/ark/handoff.md`、`docs/ark/tasks.md`、`docs/ark/plan.md`、`docs/ark/validation.md`
- 项目画像、`docs/ark/spec.md`、`docs/ark/design.md`、扩展文档索引（如存在）

## 输出
- 当前阶段判断、当前最重要的未完成项、当前阻塞项、推荐下一步动作与 Skill
- 当前最可信 / 最不可信 Artifact、用户下一步需要提供的真实配置、样例数据或外部依据（如有）

## 相关 Artifact
- 只读取 docs，不更新任何 Artifact。若发现状态需要修正，推荐 `/ark:ark-sync`、`/ark:ark-handoff` 或对应专责 Skill。

## 工作流
1. 先读取 `handoff`，了解最近一次暂停点。
2. 再读取 `tasks`，判断当前 Doing / Ready for validation / Blocked / Todo。
3. 再读取 `plan`，判断当前所在阶段。
4. 再读取 `validation`，检查是否存在未验证实现。
5. 再读取 `spec` 和 `design`，了解项目已确认的规格与架构。
6. 检查扩展文档索引、项目真实性锚点状态、核心命题与不变量承接状态。
7. 判断当前最可信和最不可信的 Artifact；若上游变更未传播或 Done 缺验证记录，优先推荐 `/ark:ark-sync` 或 `/ark:ark-validate`。
8. 依据裁决优先级序列判断下一步。
9. 给出最小但清晰的下一步建议，并说明是否需要用户提供真实配置、样例数据、凭据或外部依据。

模板占位与实质性内容判定必须遵循 `${CLAUDE_PLUGIN_ROOT}/rules/artifact-placeholder-policy.md`。不得把模板中的状态选项、示例路径、`YYYY-MM-DD` 或 `待填写` 当作真实项目状态。

`last-updated` 使用约束：
- 只把 `last-updated` 作为跨日期的粗粒度 freshness 信号
- 两个 Artifact 日期相同时，不得仅凭日期判断先后顺序
- 若发现 `last-updated` 晚于当前会话真实日期，应将对应 Artifact 标为可疑并推荐 `/ark:ark-sync`

## 裁决优先级序列

推荐策略表前，必须按以下顺序逐项裁决：

1. **判状态可信性** — Artifact 之间存在明显冲突（如 handoff 与 tasks 阶段判断相反、spec/design 与 plan/tasks 或文件现实明显冲突）→ 优先 `/ark:ark-sync`
2. **判核心命题承接** — spec/design/plan/tasks 对核心命题与不变量承接断裂或弱化 → 优先 `/ark:ark-sync`，再按原因推荐 `/ark:ark-spec`、`/ark:ark-design` 或 `/ark:ark-plan`
3. **判真实性锚点** — tasks 已推进较多但真实入口、真实依赖、真实数据源或公开契约仍无闭环，或 validation 把替身当真实通过 → 优先 `/ark:ark-sync`；若原因已明确是计划缺口 → `/ark:ark-plan`
4. **判验证闭环** — Ready for validation 项缺验证记录、Done 项缺验证记录，或当前阶段已进入验证前状态但 validation 缺记录 → 优先 `/ark:ark-validate`；Doing 项不单独触发（可能仍在进行中）
5. **判规格/设计/扩展文档更新** — 已明确是需求边界、验收标准、能力承诺变化 → `/ark:ark-spec`；已明确是模块边界、接口契约、数据流或运行机制变化 → `/ark:ark-design`；已明确是专题方案、契约、集成或数据源元信息变化 → `/ark:ark-solution`
6. **判唯一活跃执行项** — tasks 中有单一 Doing 且无阻塞 → 推进 `/ark:ark-implement`
7. **判下一个可执行 Todo** — 无 Doing 且存在依赖已满足、未阻塞的 Todo → 推荐 `/ark:ark-implement`，并明确应从第一个可执行 Todo 开始，锁定本轮唯一执行目标
8. **回退到规划层** — 以上均不满足 → 根据具体缺失选择 `/ark:ark-plan`、`/ark:ark-spec`、`/ark:ark-design`、`/ark:ark-solution` 或 `/ark:ark-intake`

## 推荐策略

| 情况 | 推荐 Skill |
|------|------------|
| handoff 与 tasks 状态矛盾 | `/ark:ark-sync` |
| spec/design 与 plan/tasks 或文件现实明显冲突 | `/ark:ark-sync` |
| 核心命题与不变量在 design/plan/tasks 中弱化或遗漏 | `/ark:ark-sync`，再按原因推荐 spec/design/plan |
| 扩展文档或 design 索引与文件现实冲突 | `/ark:ark-sync` 或 `/ark:ark-solution` |
| 真实基础设施、数据源或公开契约长期未进入闭环 | `/ark:ark-sync` 或 `/ark:ark-plan` |
| 功能已实现但无验证记录 / Ready for validation 待验证 | `/ark:ark-validate` |
| 目标清晰、Doing 明确、无阻塞 | `/ark:ark-implement` |
| 无 Doing，但存在可执行 Todo | `/ark:ark-implement`（从第一个可执行 Todo 开始，先锁定本轮唯一执行目标） |
| 当前阶段准备暂停 | `/ark:ark-handoff` |
| 需要先理解代码库再推进 | `/ark:ark-analyze` |
| 有新需求但不够清晰 | `/ark:ark-intake` |
| 需求明确但无执行计划 | `/ark:ark-plan` |
| 需要补充或更新需求规格（范围、验收、能力承诺明确变化） | `/ark:ark-spec` |
| 需要更新技术设计（模块边界、接口契约、数据流、运行机制明确变化） | `/ark:ark-design` |
| 需要补充专题方案、接口契约、集成或数据源元信息 | `/ark:ark-solution` |
| 实现已完成，合并前需评审 | `/ark:ark-review` |

## 固定输出格式

### 1. 当前阶段
### 2. 当前最重要的未完成项
### 3. 当前阻塞
### 4. 真实性锚点状态
### 5. Artifact 可信度
- 当前最可信：
- 当前最不可信：
### 6. 用户需提供的信息
- 无 / 配置 / 样例数据 / 凭据 / 外部依据 / 审查意见
### 7. 推荐下一步
### 8. 推荐 Skill

## 备注
`/ark:ark-next` 不是重新做全套规划，而是帮助在当前状态下找到最合理的下一步。
