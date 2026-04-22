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

## 输出
- 当前阶段判断、当前最重要的未完成项、当前阻塞项、推荐下一步动作与 Skill

## 相关 Artifact
- 主要读取 docs，仅在极少数情况下做小幅状态澄清

## 工作流
1. 先读取 `handoff`，了解最近一次暂停点。
2. 再读取 `tasks`，判断当前 Doing / Blocked / Todo。
3. 再读取 `plan`，判断当前所在阶段。
4. 再读取 `validation`，检查是否存在未验证实现。
5. 再读取 `spec` 和 `design`，了解项目已确认的规格与架构。
6. 依据裁决优先级序列判断下一步。
7. 给出最小但清晰的下一步建议。

## 裁决优先级序列

推荐策略表前，必须按以下顺序逐项裁决：

1. **判状态可信性** — Artifact 之间存在明显冲突（如 handoff 与 tasks 阶段判断相反）→ 优先 `/ark:ark-sync`
2. **判验证闭环** — Done 项缺验证记录，或当前阶段已进入验证前状态但 validation 缺记录 → 优先 `/ark:ark-validate`；Doing 项不单独触发（可能仍在进行中）
3. **判唯一活跃执行项** — tasks 中有单一 Doing 且无阻塞 → 推进 `/ark:ark-implement`
4. **回退到规划层** — 以上均不满足 → 根据具体缺失选择 `/ark:ark-plan`、`/ark:ark-spec`、`/ark:ark-design` 或 `/ark:ark-intake`

## 推荐策略

| 情况 | 推荐 Skill |
|------|------------|
| handoff 与 tasks 状态矛盾 | `/ark:ark-sync` |
| 功能已实现但无验证记录 | `/ark:ark-validate` |
| 目标清晰、Doing 明确、无阻塞 | `/ark:ark-implement` |
| 当前阶段准备暂停 | `/ark:ark-handoff` |
| 需要先理解代码库再推进 | `/ark:ark-analyze` |
| 有新需求但不够清晰 | `/ark:ark-intake` |
| 需求明确但无执行计划 | `/ark:ark-plan` |
| 需要补充或更新需求规格 | `/ark:ark-spec` |
| 需要更新技术设计 | `/ark:ark-design` |
| 实现已完成，合并前需评审 | `/ark:ark-review` |

## 固定输出格式

### 1. 当前阶段
### 2. 当前最重要的未完成项
### 3. 当前阻塞
### 4. 推荐下一步
### 5. 推荐 Skill

## 备注
`/ark:ark-next` 不是重新做全套规划，而是帮助在当前状态下找到最合理的下一步。
