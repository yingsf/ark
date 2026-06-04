---
name: capability-policy
description: ARK 依赖能力及降级策略，确保工作流在不同环境下可正常运行
---

# 能力降级策略

## 核心能力

| 能力 | 依赖的 Skill | 不可用时降级 |
|------|-------------|-------------|
| Agent tool | implement, analyze, validate | 单上下文顺序执行 |
| git | implement (checkpoint), sync (freshness) | 跳过 checkpoint / 跳过 git 历史对比，可信度改用文件现实、Artifact 一致性和验证记录判断 |
| uv | init, validate | 退回 pip |
| pytest | test, validate | 跳过自动测试 |
| ruff | implement (batch) | 跳过 ruff check |
| pyright | implement (batch) | 跳过类型检查 |

## 探测策略

- **ark-init**：Mode A 记录能力快照到宿主上下文文件（Claude Code: `CLAUDE.md`；Codex: `AGENTS.md`，5-8 行，标注"仅初始化时参考"）；Mode B 若宿主上下文文件已存在，仅在用户确认后更新，否则只在输出摘要中报告当前探测结果
- **各 Skill 入口**：按需重新检查关键能力，不依赖初始化快照
- **Agent tool**：在 Skill 执行时检查当前工具集是否包含 Agent，不靠 shell 探测
- **能力变化不阻塞工作流**，只影响功能完整性

## 降级原则

- 降级不打断用户流程，但必须在输出中说明跳过了哪些检查/步骤
- 不因能力缺失而降低质量标准（如没 ruff 不能跳过代码质量，只是不做自动格式化）
- Sub-agent 不可用时，输出固定格式降级说明（见 sub-agent-protocol.md）

## sub-agent 降级输出格式

当 Agent tool 不可用或未启用 sub-agent 模式时，Skill 输出中必须包含：

```
Sub-agent 状态：未启用
原因：当前环境未提供 Agent tool / 任务规模不需要 / 用户禁用
降级影响：context rot 风险较高，建议按 batch 收口，及时 handoff
```

当 sub-agent 模式正常启用时，输出中记录：

```
Sub-agent 状态：已启用（N 个 worker / reader / collector）
```
