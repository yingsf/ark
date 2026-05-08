<!-- ark-artifact: handoff -->
<!-- schema-version: 1.0 -->

# Handoff

<!-- 本文件是恢复视图，不是执行主文档。-->
<!-- 目标：让下一次继续的人（或自己）在 5 分钟内恢复到可执行状态。-->
<!-- 不要用它代替 plan 作为执行主文档，不要用它代替 tasks 管理状态。-->

## 上次更新时间
YYYY-MM-DD

## 当前目标
<!-- 当前阶段的大目标是什么 -->

## 当前阶段
<!-- 澄清 / 规划 / 实现 / 验证 / 收尾 -->

## 已完成
- 项目 1
- 项目 2

## 未完成
<!-- 对大改动中的未完成任务，应记录当前批次已完成到哪个文件/锚点。-->
- 项目 1
- 项目 2

## 风险 / 阻塞
- 风险或阻塞 1（解除条件：...）
- 风险或阻塞 2

## Artifact 信任状态
<!-- 对每个核心 Artifact 标注可信度（fresh / stale / conflicting / unknown），帮助 next 判断应优先读取哪个 -->
- `docs/ark/spec.md`：fresh / stale / conflicting / unknown
- `docs/ark/design.md`：fresh / stale / conflicting / unknown
- `docs/ark/plan.md`：fresh / stale / conflicting / unknown
- `docs/ark/tasks.md`：fresh / stale / conflicting / unknown
- `docs/ark/decisions.md`：fresh / stale / conflicting / unknown
- `docs/ark/validation.md`：fresh / stale / conflicting / unknown

## 恢复顺序
<!-- 明确下次会话的恢复动作序列，比"关键文件"更强 -->
1. 先读 `docs/ark/{artifact}` — 原因
2. 再读 `docs/ark/{artifact}` — 原因
3. 然后执行 {动作}

## 推荐下一步
- 下一步动作 1
- 下一步动作 2

## 推荐 Skill
`/ark:ark-implement`
<!-- 或 /ark:ark-validate / /ark:ark-sync / /ark:ark-debug 等 -->

## 恢复提示
<!-- 下一次继续时最先要知道的上下文，写最关键的 1-3 条 -->
