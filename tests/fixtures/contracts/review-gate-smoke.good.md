# Review Gate Smoke Good Fixture

## External Review Gate

### High-risk immediate
- Gate 结论：immediate
- 风险等级：High
- 命中规则：CI/发布/安装/更新路径
- 当前 batch：无
- 是否建议继续下一个 task：否
- 外部审查状态：pending
- 下一步：/ark:ark-review-gate prepare

### Low-risk batch candidate
- Gate 结论：batch-candidate
- 风险等级：Low
- 命中规则：同一功能闭环，本地相关测试通过，不改公共接口
- 当前 batch：T1, T2
- 是否建议继续下一个 task：是
- 外部审查状态：pending
- 下一步：继续下一个同闭环低风险 task

### Batch ready
- Gate 结论：batch-ready
- 风险等级：Low
- 命中规则：达到 3 tasks 上限
- 当前 batch：T1, T2, T3
- 触发上限：3 tasks
- 是否建议继续下一个 task：否
- 外部审查状态：package-prepared
- 下一步：/ark:ark-review-gate prepare

### Findings imported
- Gate 结论：immediate
- 风险等级：High
- Findings 分类：必须修复 / 可延期 / 不处理
- 外部审查状态：findings-imported
- 下一步：/ark:ark-debug

### Recheck pending
- Gate 结论：immediate
- 风险等级：High
- 外部审查状态：recheck-pending
- 下一步：/ark:ark-review-gate recheck

### Gate passed
- Gate 结论：immediate
- 风险等级：High
- 外部审查状态：passed
- 下一步：/ark:ark-validate

## Boundary Assertions
- source code：不修改
- validation.md：不写入，建议由 /ark:ark-validate 记录
- tasks.md：不标记 Done
