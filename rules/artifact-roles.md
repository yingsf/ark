# Artifact 职责速查

每个 Artifact 主要回答一个问题。写入时先判断「这条内容回答的是哪个问题」，再选择对应文件。

| Artifact | 回答的问题 | 主更新者 | 不应用于 |
|----------|-----------|----------|----------|
| `docs/ark/spec.md` | 要做什么 | `/ark:ark-spec`（可由 `/ark:ark-analyze` 预填充）| 记录实施步骤、任务状态、测试结果 |
| `docs/ark/design.md` | 准备怎么做 | `/ark:ark-design`（可由 `/ark:ark-analyze` 预填充）| 记录执行进度、细碎任务清单、最终验证结果 |
| `docs/ark/plan.md` | 将如何分阶段推进 | `/ark:ark-plan`（也可由 implement、debug、sync 回写）| 代替 tasks 管理细粒度状态、代替 handoff 做恢复摘要 |
| `docs/ark/tasks.md` | 当前有哪些任务，分别处于什么状态 | `/ark:ark-tasks`（也可由 implement、debug、sync 小幅更新）| 代替 spec 定义需求、代替 plan 定义阶段策略 |
| `docs/ark/decisions.md` | 关键选择是什么，为什么这么选 | `/ark:ark-decide` | 记录执行进度、记录验证结果 |
| `docs/ark/validation.md` | 验证了什么，证据是什么 | `/ark:ark-validate` | 记录「准备验证什么」（那是 plan 的职责）|
| `docs/ark/handoff.md` | 下次从哪里继续 | `/ark:ark-handoff` | 代替 plan 作为主执行文档、代替 tasks 管理状态 |

## 核心约束

- **不得混用**：每个 Artifact 主要回答一个问题，不应将多个职责写入同一文件
- **冲突必须先显式化**：发现文档与代码现实不符时，必须先指出冲突，再修正，不得直接跳过
- **没有验证记录，不宣称完成**：中大型任务如无 `docs/ark/validation.md` 记录，不得写出「已完成且无风险」的结论
- **过期文档必须说明**：如果 Artifact 长期未维护，必须明确标注其陈旧状态，不得假装有效

## 一句话规则

`spec` 管目标 · `design` 管方案 · `plan` 管推进 · `tasks` 管状态 · `decisions` 管取舍 · `validation` 管证据 · `handoff` 管恢复

## Design vs Decide 边界

- **design.md**：记录方案如何工作，以及局部技术权衡
- **decisions.md**：只记录满足以下全部条件的选择——不可逆或高回退成本、影响长期维护方向、未来可能被团队质疑或推翻

一般性技术权衡留在 design.md，不重复进 decisions.md。触发 ark-decide 时需判断：如果该选择在 3 个月内不太可能被重新审视，留 design.md 即可。

## Artifact 可信度

四态定义：

| 状态 | 定义 |
|------|------|
| fresh | 内容与文件现实 / Artifact 一致性 / 验证记录一致 |
| stale | 最近代码变更影响该 Artifact，但 Artifact 未反映 |
| conflicting | Artifact 之间描述矛盾 |
| unknown | 缺少足够证据判断 |

判断依据（按优先级）：

1. 当前文件现实
2. Artifact 之间一致性
3. 已执行验证记录
4. git diff / git log（如可用）

无 git 的项目依据 1-3 即可判断，不必然 unknown。

关键 Skill 入口要求：
- ark-implement：开始前检查 plan.md + tasks.md 可信度；实现后检查本次改动是否引发 spec.md / design.md 漂移
- ark-validate：检查 tasks.md 可信度
- ark-next：检查 handoff.md + tasks.md + plan.md 可信度；若 spec.md / design.md 明显 stale 或 conflicting，应优先推荐 ark-sync
- ark-sync：输出完整 Artifact 可信度矩阵，包括 spec.md / design.md；对 spec/design 只建议对应 Skill，不直接修正
- 非 fresh 时推荐 ark-sync

> 完整的回写条件与禁止性约束见 `${CLAUDE_PLUGIN_ROOT}/rules/artifact-update-policy.md`
