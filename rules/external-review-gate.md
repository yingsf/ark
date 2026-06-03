# External Review Gate

本规则定义 ARK 与外部智能体代码审查协作时的门禁策略。目标是保留跨智能体深度审查的质量收益，同时避免每个低风险 task 都触发完整外部审查。

## 核心原则

- **高风险不过夜**：命中高风险条件的 task 必须立即外部审查，不进入 batch。
- **低风险不单审**：低风险、同闭环 task 可以进入小批量审查队列。
- **小批量有上限**：batch 不是无限积攒，达到任一上限必须停下外部审查。
- **复检不扩域**：修复后复检默认只检查上一轮 findings 是否闭合，以及修复是否引入明显回归。
- **review 不替代 validate**：外部审查通过只是验证证据的一部分，最终 Done 仍由 `/ark:ark-validate` 记录。

## Gate 结论

| 结论 | 含义 | 下一步 |
|------|------|--------|
| `immediate` | 当前 task 必须立即外部审查 | 生成外部审查包，不建议继续下一个 task |
| `batch-candidate` | 当前 task 可进入低风险审查 batch | 记录 pending，允许继续下一个同闭环低风险 task |
| `batch-ready` | batch 已到上限或闭环结束 | 生成 batch 外部审查包 |
| `blocked` | 材料不足或状态冲突，无法判断 | 先 `/ark:ark-sync`、补充信息或收口当前状态 |

## 必须立即外部审查

只要命中任一条件，结论为 `immediate`：

- 认证、权限、安全、隐私、敏感数据。
- 支付、账务、额度、扣费、退款。
- 数据删除、数据迁移、不可逆写入。
- 数据库 schema、索引、迁移脚本。
- 公共 API、接口协议、返回结构、错误码。
- 并发、事务、缓存、幂等、重试。
- 跨模块共享基础设施。
- CI、发布、安装、更新路径。
- 新增依赖或升级关键依赖。
- 本 task 实现过程中测试失败过。
- `/ark:ark-implement` 明确输出风险、不确定点或替身边界影响可信度。
- 上一轮外部审查发现 Critical / Major，且本 task 属于相同区域。
- 改动范围明显偏大，例如跨多个子系统。

## 可以进入小批量审查

必须同时满足以下条件，才可判为 `batch-candidate`：

- 与当前 batch 中 task 属于同一个功能闭环、同一 batch、同一真实入口或同一公开契约。
- 不改公共接口、数据库 schema、权限、安全、支付、隐私或共享基础设施。
- 本地相关测试通过，且没有未解释的失败。
- 改动范围小，需求和实现方向清楚。
- 没有明显不确定点、替身冒充真实验证或设计漂移。

## Batch 上限

任一条件达到即结论为 `batch-ready`：

- 最多 3 个 task。
- 最多 90 分钟实现量。
- 最多 1 个功能闭环。
- 最多 500 行核心 diff。
- 用户要求停下审查。
- 当前 batch 中任一 task 后续被发现命中 immediate 条件。

## 外部审查包边界

审查包必须包含：

- task ID / batch task 列表。
- 用户可观察目标与完成信号。
- 相关 `spec.md`、`design.md`、`plan.md`、`tasks.md` 摘要。
- 本次改动文件和核心 diff 摘要。
- 已执行测试及结果。
- 已知风险、替身边界和未覆盖项。
- 要求外部智能体重点检查的范围。
- 明确不要扩展审查的范围。

## Findings 导入边界

外部 findings 导入后必须分类：

- **必须修复**：真实 bug、契约偏差、影响 task 验收的问题、关键测试缺口。
- **可延期**：非当前 task 的重构建议、低风险 craftsmanship、后续增强。
- **不处理**：误报、与本轮目标无关、已被现有证据覆盖且无实际风险。

`/ark:ark-debug` 只应修复“必须修复”项。若要处理“可延期”项，必须成为新的明确 task 或用户明确要求。

## Validation 约束

若 task 已进入 external review gate，但没有外部审查通过证据或 findings 复检通过证据，`/ark:ark-validate` 不得将其标记为 Done。

可以记录为：

```text
本地验证通过，但外部 review pending。
任务状态保持 Ready for validation。
```

Done 必须同时满足：

- 本地验证通过。
- 外部 review 通过，或 findings 已修复并复检通过。
- `validation.md` 记录外部审查 evidence、覆盖任务和覆盖原因。

## Handoff 约束

当存在 pending 外部审查 batch 时，必须在 `docs/ark/handoff.md` 的 External Review Gate 区域记录：

- gate 结论。
- pending task。
- batch 范围。
- 触发上限。
- 外部审查状态。
- 下一步动作。
