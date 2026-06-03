---
name: ark-helper
description: |
  ARK 轻量问答和通用流程说明。解释概念、场景和 Skill 用法。
  触发时机：想知道 ARK 怎么用、某个 Skill 适用什么场景、通用流程是什么。
  关键词：帮助、helper、怎么用、用什么指令、流程、场景、指引、概念、解释。
version: "2.0"
---

# /ark-helper

## 目标

回答关于 ARK 工作流的概念性问题和通用流程说明。帮助用户理解 ARK 的设计、Skill 的适用场景和 Artifact 之间的关系。

**硬约束：本 Skill 只负责概念解释和通用流程说明，不读取当前项目状态，不裁决下一步，不更新任何 Artifact。**

## 适用场景

- 想知道"ARK 怎么用"
- 想了解某个 Skill 的适用场景和工作方式
- 想了解 Artifact 之间的关系
- 想了解某类任务的通用推荐流程

## 不适用场景

- 需要读取当前项目状态并推荐下一步（那是 ark 或 ark-next）
- 需要修复 Artifact 状态失真（那是 ark-sync）
- 需要执行具体工作（那是其他 Skill 的职责）

## 前置建议

- 无前置要求，随时可执行

## 输入

- 用户的问题（关于 ARK 工作流的概念性问题）

## 输出

- 概念解释或通用流程说明

## 相关 Artifact

- **不读取任何 Artifact**
- **不更新任何 Artifact**

## 工作流

1. **理解用户问题**：判断用户想了解的是概念、流程还是 Skill 选择
2. **提供解释**：基于 ARK 的设计原则给出清晰的说明
3. **必要时给出通用流程示例**（如"修 bug 通常走 debug → implement → test → validate"）

## 常见问题参考

### ARK 怎么用？

ARK 通过路由倾向工作：描述你的任务，Claude 会优先倾向匹配对应的 ARK Skill；未触发时可使用 `/ark:ark` 查看项目状态和推荐，或直接调用 `/ark:ark-xxx` 进入特定 Skill。

### 什么时候该用哪个 Skill？

- 新需求 / 不确定要做什么 → ark-intake
- 修 bug / 排查错误 → ark-debug
- 写代码 / 实现功能 → ark-implement
- 跨智能体外部审查门禁 / Codex 审查包 / findings 导入 → ark-review-gate
- 审查代码变更 → ark-review
- 不确定下一步 → ark（查看状态）或 ark-next（裁决下一步）
- 写专题方案、接口契约、集成或数据源元信息 → ark-solution

`ark-intake` 只负责澄清、分流和建议落盘位置，不直接写入 Artifact；正式写入由 `ark-spec`、`ark-plan` 等对应 Skill 完成。

### 核心 Artifact 各自管什么？

- spec.md — 要做什么（目标和范围）
- design.md — 准备怎么做（技术方案）
- plan.md — 分几个阶段推进
- tasks.md — 当前有哪些任务、各什么状态
- decisions.md — 关键选择和取舍理由
- validation.md — 验证了什么、证据是什么
- handoff.md — 下次从哪里继续

扩展文档不属于 7 个核心 Artifact。详细方案、专题设计、契约、集成和数据源元信息由 `ark-solution` 写入项目自有目录，例如 `docs/solution/`、`docs/contracts/`、`docs/data-sources/`。

### 小任务和大任务流程有什么区别？

- Small：intake → implement/debug → test → validate
- Medium：intake → design/solution（如需要）→ plan → implement → test → validate
- Large：init → spec → design → solution（按需）→ plan → tasks → implement → test → validate → handoff

### 接手一个已有项目怎么开始？

1. ark-init Mode B（植入工作流，不碰代码）
2. ark-analyze（扫描代码库，建立全局认知）
3. ark-spec / ark-design（审查确认 analyze 的预填充结果）
4. ark-solution（如需要专题方案、契约、集成或数据源元信息）
5. ark-plan（制定推进计划）

### ark-solution 和 ark-design 有什么区别？

- `ark-design` 维护 `docs/ark/design.md`，负责全局设计摘要、模块边界和扩展文档索引。
- `ark-solution` 维护项目自有扩展文档，负责专题详细方案、详细设计、接口契约、集成说明和数据源元信息。
- `ark-solution` 不直接修改 `docs/ark/*`；如果全局摘要或索引需要同步，它会建议后续执行 `ark-design`。

### ark-review 和 ark-review-gate 有什么区别？

- `ark-review` 是 Claude Code 内部深度契约代码审查。
- `ark-review-gate` 组织跨智能体外部审查流程：判断当前 task 是立即去外部审查，还是进入同闭环低风险 batch；生成外部审查包；导入外部 findings；生成修复后的定向复检包。
- 如果你采用外部 Codex 审查，推荐流程是 `ark-implement → ark-review-gate prepare → 外部审查 → ark-review-gate import → ark-debug → ark-review-gate recheck → ark-validate`。

### ARK 会管理 data 目录吗？

不会。数据由项目自己管理，可能在本地目录、对象存储、测试夹具或外部系统中。ARK 只记录数据源元信息、脱敏状态、样例范围和验证证据，不托管数据内容。

## 与其他 Skill 的区别

- **ark**：读取当前项目状态并推荐下一步。helper 不读状态。
- **ark-next**：基于完整 Artifact 状态做决策链判断。helper 不做裁决。
- **ark-sync**：检查并修复 Artifact 状态失真。helper 不检查状态。

## 验证要求

- 解释必须基于 ARK 的实际设计，不得编造规则或流程
- 通用流程必须引用 ARK 已定义的合法 Skill
- 不得读取任何当前项目 Artifact
- 不得推荐特定于当前项目的下一步
- 不得更新任何 Artifact

## 停止条件

- 用户的问题已被回答

## 固定输出格式

### 1. 问题理解
一句话说明你在问什么。

### 2. 回答
概念解释或通用流程说明。

### 3. 进一步了解（可选）
若问题涉及多个方面，列出相关的可进一步了解的主题。
