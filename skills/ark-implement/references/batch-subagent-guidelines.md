# Batch / Sub-agent Guidelines

本文件承载 `/ark:ark-implement` 的批次实施、sub-agent、checkpoint 和中断安全细则。Medium/Large 任务、显式功能 Batch、触发批次信号或使用 sub-agent 时读取。

## 批次触发信号

出现以下任一信号时，应优先考虑批次实施：

- 涉及 3 个以上文件
- 单文件大段重写，非增删个别函数
- 存在明显顺序依赖，必须先完成 A 才能做 B
- 预期单次修改难以在一个稳定回合内完成

## 批次硬约束

- 触发批次信号时，不得默认一次完成全部修改；应先拆成实施批次，并只完成当前批次
- 未指定 task、batch 或阶段范围时，不得连续执行多个 Todo；每轮默认只推进一个 task 或一个明确 batch
- batch 覆盖多个 task 时，必须在编码前声明覆盖任务、合并原因、统一验证计划和批次边界
- 覆盖多个 task 的批次仅限同一功能交付单元、技术闭环、真实入口或公开契约

## 批次四要素

| 要素 | 含义 |
|------|------|
| 本批目标 | 这一 batch 要达成什么 |
| 涉及文件 | 本批改动哪些文件 |
| 修改锚点 | 每个文件中改哪一段 / 哪一类调用点 |
| 完成信号 | 这一 batch 什么时候算做完 |

## 执行规则

- 每次只执行一个批次
- 当前批次可以覆盖多个 task 仅限：用户明确指定多个 task、tasks.md 已记录当前批次、plan 明确声明该阶段作为一个 batch、或多个 task 不可独立验证必须合并执行
- 覆盖多个 task 的批次必须声明当前批次、覆盖任务、合并原因、统一验证计划、批次边界
- 每个批次结束后执行局部质量整理和检查（ruff check --fix + ruff format 仅限已改 Python 文件，pyright 按项目能力执行）
- 每个批次结束后检查新增/修改的公共接口、关键方法和复杂逻辑是否满足注释/docstring 要求
- 每个批次结束后更新 Reality Check 结果：真实锚点已推进 / 仍为替身 / 无直接锚点，并记录退出条件
- ruff lint fix 只在批次完成、当前修改已处于稳定点时执行；编辑中的 PostToolUse hook 只负责 format，不负责 lint fix
- 若 ruff check --fix 修改了文件，必须重新读取受影响文件或 diff
- 更新 `docs/ark/tasks.md` 记录批次进展
- 输出当前批次完成状态，建议下一批次或停止

## Sub-agent Batch 模式

Medium/Large 任务可启用 batch sub-agent 模式缓解 context rot：

1. 检查 Agent tool 是否可用
   - 可用：每个 batch spawn 独立 sub-agent
   - 不可用：单上下文顺序执行，输出降级说明
2. sub-agent 遵循 `${CLAUDE_PLUGIN_ROOT}/rules/sub-agent-protocol.md`
   - 只写 batch write set 内的源文件
   - 不写 docs/ark/*
3. Write Set 审计
   - 执行前：主 agent 记录 batch write set
   - 执行后：检查 diff 是否超出 write set
   - 越界：停止并报告，列出意外修改的文件，不自动合并
   - 正常：复核通过后主 agent 更新 Artifact
4. batch 完成后主 agent 复核 diff、运行局部质量整理、更新 tasks.md、进入 Checkpoint 建议

降级输出：

```text
Sub-agent 状态：未启用
原因：当前环境未提供 Agent tool
降级影响：context rot 风险较高，建议按 batch 收口，及时 handoff
```

正常启用时：

```text
Sub-agent 状态：已启用（N 个 worker）
```

## 中断安全

- 批次完成点是天然的中断安全点：当前批次所有文件修改已落盘、局部检查已执行、已知未完成内容已列清
- 若未到达批次完成点且会话即将中断，优先完成当前批次再 handoff
- 若确实无法完成当前批次，handoff 必须记录已完成文件/锚点、未完成文件/锚点、下一批次入口

## Checkpoint 建议

每个 batch 完成后，根据任务大小决定 checkpoint 条件：

- Small 任务：batch 完成后可选 checkpoint commit
- Medium/Large 任务：batch 完成、相关 test 子集通过、validate evidence 草稿可用后建议 checkpoint commit

commit 范围：该 batch 修改的文件

commit 格式：`<type>(<scope>): <batch-goal>`

不自动提交，等用户确认

每个完成点的输出必须给出：

- 建议 checkpoint commit：是 / 否
- 建议 message：
- 建议纳入文件：
- 不建议纳入文件：
