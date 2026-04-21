# 任务规模快速判断

## 默认规模假设

当没有足够上下文判断规模时，默认按 **medium** 处理，宁可轻微过度规划，不可草率执行。

## 三档规模

| 规模 | 典型特征 | 推荐流程 |
|------|---------|----------|
| **Small** | 目标清晰、影响范围小、通常只涉及 1 个文件、可在单会话完成、低风险 | `intake → implement/debug → test → validate` |
| **Medium** | 多文件或单模块范围、需要分步骤执行、可能跨会话、有一定风险 | `intake → plan → design（如结构复杂）→ implement → test → validate` |
| **Large** | 多模块或多阶段、架构影响、高风险或高返工成本、需要完整恢复能力 | `intake → spec → design → plan → tasks → implement → test → validate → handoff` |

> Medium 中的 `design` 是有条件可选：若改动涉及新模块、接口边界或架构决策，应执行；否则可跳过。

## 一句话判断法

- 担心「中断后会不会忘」→ 至少 medium
- 担心「改错后代价很大」→ 至少 medium
- 担心「以后为什么这么做会说不清」→ 接近 large

## 升级信号（出现任一即应升级）

**Small → Medium：**
- 改动开始跨多个文件
- 需要分步骤执行
- 会话可能中断后继续
- 风险高于预期

**Medium → Large：**
- 出现架构级影响
- 需要正式规格文档或决策记录
- 任务将持续多个阶段
- 多模块协调成为主要难点

## 降级条件（需同时满足所有条件）

**Large → Medium：** 需求显著收敛 + 实际改动范围明显小于预期 + 不再需要完整 Artifact 追踪 + 风险已明显下降

**Medium → Small：** 已收敛为单点修改 + 不再需要分步骤 + 验证路径清晰且短 + 中断恢复成本很低

> 完整的判定规则见 `${CLAUDE_PLUGIN_ROOT}/rules/task-sizing-rules.md`
