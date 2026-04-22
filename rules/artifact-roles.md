# Artifact 职责速查

每个 Artifact 主要回答一个问题。写入时先判断「这条内容回答的是哪个问题」，再选择对应文件。

| Artifact | 回答的问题 | 主更新者 | 不应用于 |
|----------|-----------|----------|----------|
| `docs/ark/spec.md` | 要做什么 | `/ark-spec`（可由 `/ark-analyze` 预填充）| 记录实施步骤、任务状态、测试结果 |
| `docs/ark/design.md` | 准备怎么做 | `/ark-design`（可由 `/ark-analyze` 预填充）| 记录执行进度、细碎任务清单、最终验证结果 |
| `docs/ark/plan.md` | 将如何分阶段推进 | `/ark-plan`（也可由 implement、debug、sync 回写）| 代替 tasks 管理细粒度状态、代替 handoff 做恢复摘要 |
| `docs/ark/tasks.md` | 当前有哪些任务，分别处于什么状态 | `/ark-tasks`（也可由 implement、debug、sync 小幅更新）| 代替 spec 定义需求、代替 plan 定义阶段策略 |
| `docs/ark/decisions.md` | 关键选择是什么，为什么这么选 | `/ark-decide` | 记录执行进度、记录验证结果 |
| `docs/ark/validation.md` | 验证了什么，证据是什么 | `/ark-validate` | 记录「准备验证什么」（那是 plan 的职责）|
| `docs/ark/handoff.md` | 下次从哪里继续 | `/ark-handoff` | 代替 plan 作为主执行文档、代替 tasks 管理状态 |

## 核心约束

- **不得混用**：每个 Artifact 主要回答一个问题，不应将多个职责写入同一文件
- **冲突必须先显式化**：发现文档与代码现实不符时，必须先指出冲突，再修正，不得直接跳过
- **没有验证记录，不宣称完成**：中大型任务如无 `docs/ark/validation.md` 记录，不得写出「已完成且无风险」的结论
- **过期文档必须说明**：如果 Artifact 长期未维护，必须明确标注其陈旧状态，不得假装有效

## 一句话规则

`spec` 管目标 · `design` 管方案 · `plan` 管推进 · `tasks` 管状态 · `decisions` 管取舍 · `validation` 管证据 · `handoff` 管恢复

> 完整的回写条件与禁止性约束见 `${CLAUDE_PLUGIN_ROOT}/rules/artifact-update-policy.md`
