# 任务规模快速判断

## 默认规模假设

当没有足够上下文判断规模时，默认按 **medium** 处理，宁可轻微过度规划，不可草率执行。

## 三档规模

| 规模 | 典型特征 | 推荐流程 |
|------|---------|----------|
| **Small** | 目标清晰、影响范围小、通常只涉及 1 个文件、可在单会话完成、低风险 | `intake → implement/debug → test → validate` |
| **Medium** | 多文件或单模块范围、需要分步骤执行、可能跨会话、有一定风险 | `intake → design/solution（如需要）→ plan → implement → test → validate` |
| **Large** | 多模块或多阶段、架构影响、高风险或高返工成本、需要完整恢复能力 | `intake → spec → design → solution（按需）→ plan → tasks → implement → test → validate → handoff` |

> Medium 中的 `design/solution` 是有条件可选：若改动涉及新模块、接口边界、架构决策、专题方案、契约、集成或数据源元信息，应先补齐对应设计/扩展文档，再让 plan 拆执行步骤；否则可跳过。
> 当任务需要专题详细方案、接口契约、集成说明或数据源元信息时，使用 `ark-solution` 写入项目自有扩展文档。
> 流程中的 Artifact 落盘由对应 Skill 完成；`intake` 只负责澄清、分流和建议落盘位置，不直接写入 `docs/ark/*`。

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
- 需要真实入口、真实依赖、真实数据源或公开契约来判断完成

**Medium → Large：**
- 出现架构级影响
- 需要正式规格文档或决策记录
- 任务将持续多个阶段
- 多模块协调成为主要难点
- 真实基础设施、数据源或跨系统契约成为主要风险

## 降级条件（需同时满足所有条件）

**Large → Medium：** 需求显著收敛 + 实际改动范围明显小于预期 + 不再需要完整 Artifact 追踪 + 风险已明显下降

**Medium → Small：** 已收敛为单点修改 + 不再需要分步骤 + 验证路径清晰且短 + 中断恢复成本很低

> 完整的判定规则见 `${CLAUDE_PLUGIN_ROOT}/rules/task-sizing-rules.md`
