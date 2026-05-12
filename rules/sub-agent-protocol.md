---
name: sub-agent-protocol
description: sub-agent 写权限隔离、输出格式、复核流程，确保主 agent 是唯一状态合并者
---

# Sub-agent 协议

## 适用范围

ark-analyze (scanner)、ark-validate (evidence collector)、ark-implement (batch worker)、ark-solution（仅在主 agent 明确分配独立扩展文档写集时）

## 写权限

| sub-agent 角色 | 允许写 | 禁止写 |
|---------------|--------|--------|
| analyze scanner | 无（只返回结果） | 所有文件 |
| validate collector | 无（只返回结果） | 所有文件 |
| implement worker | batch write set 内的源文件 | docs/ark/*、.claude/*、write set 外的文件 |
| solution writer | 明确分配的扩展文档 write set | docs/ark/*、源代码、write set 外的文件 |

统一规则：**任何 sub-agent 不写 docs/ark/* 下任何文件。所有核心 Artifact 由主 agent 统一写入。**

扩展文档虽可由 `ark-solution` 管理，但 sub-agent 只能在主 agent 明确指定的扩展文档 write set 内写入，且不得写项目数据内容。

## Write Set 审计（implement worker / solution writer）

每个 batch 执行前：
1. 主 agent 记录 **batch write set**（该 batch 声明要修改的文件列表）

batch sub-agent 完成后：
2. 主 agent 检查 diff
3. diff 中文件 ⊆ write set → 正常，复核变更
4. diff 中文件 ⊄ write set → **停止并报告越界**，列出意外修改的文件，不自动合并
5. 复核通过 → 主 agent 更新 Artifact

analyze scanner / validate collector 不写文件，无需 write set。

## 输出格式

所有 sub-agent 返回结构化 summary：

- **changed_files**：修改的文件列表（仅 implement worker）
- **findings**：发现的事实 / 证据
- **assumptions**：执行期间做的假设
- **test_results**：测试执行结果（如有）

## 复核流程

1. sub-agent 完成 → 返回 summary
2. 主 agent 检查 diff（如有文件修改）
3. 主 agent 确认变更符合预期
4. 主 agent 统一更新 Artifact

## 降级

Agent tool 不可用 → 不 spawn sub-agent，单上下文执行。

降级时 Skill 输出中必须包含：

```
Sub-agent 状态：未启用
原因：当前环境未提供 Agent tool / 任务规模不需要 / 用户禁用
降级影响：context rot 风险较高，建议按 batch 收口，及时 handoff
```

正常启用时输出中记录：

```
Sub-agent 状态：已启用（N 个 worker / reader / collector）
```
