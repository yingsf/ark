---
name: ark
description: |
  ARK 显式智能入口。读取项目 Artifact 状态，判断当前阶段并推荐下一步。
  触发时机：不确定该做什么、接手项目、想查看当前进度。
  关键词：ark、入口、该做什么、当前状态、项目进度、推荐、下一步。
version: "1.0"
---

# /ark

## 目标

为用户提供显式的项目状态读取和下一步推荐。当用户不确定该做什么时使用。

主要路由由 rules/ark.md 的自动路由倾向处理，本 Skill 是辅助入口——在自动路由未触发时提供显式的状态感知和推荐。

**硬约束：本 Skill 只负责状态读取和路径推荐，不自动执行任何后续 Skill，不更新任何 Artifact。**

## 适用场景

- 用户说"帮我看看该做什么"
- 用户说"接手这个项目"
- 用户不确定当前进度和下一步
- 用户主动输入 /ark:ark

## 不适用场景

- 用户意图明确（自动路由已处理）
- 用户已直接调用 /ark:ark-xxx

## 前置建议

- 无前置要求，随时可执行

## 输入

- 用户的问题或场景描述（可选）
- `docs/ark/` 下所有 Artifact（按优先级读取）

## 输出

- 项目状态报告
- 推荐下一步（1-2 个选项 + 理由）

## 相关 Artifact

- 读取：handoff.md > tasks.md > plan.md > validation.md > spec.md/design.md > 扩展文档索引
- **不更新任何 Artifact**

## 工作流

1. **检查项目是否已初始化**
   - 检查 docs/ark/ 下是否存在 Artifact
   - 不存在 → 推荐 ark-init（新项目用 Mode A，已有项目用 Mode B）
   - 已有项目但未初始化 → 先 ark-init Mode B 植入工作流，再 ark-analyze

2. **读取 Artifact 状态**
   - 优先级：handoff.md > tasks.md > plan.md > validation.md > spec.md/design.md
   - 判断每个关键 Artifact 的可信度（fresh/stale/conflicting/unknown）
   - 检查 `docs/ark/design.md` 中是否存在扩展文档索引，必要时查看索引目标是否存在
   - 检查项目画像和真实性锚点是否能解释当前 plan/tasks/validation

3. **输出状态报告**

   ### 项目状态
   - 当前阶段：<从 Artifact 推断>
   - Artifact 可信度：<列出非 fresh 的 Artifact>
   - 活跃任务：<从 tasks.md 读取 Doing 状态的任务>
   - 阻塞项：<从 tasks.md 读取 Blocked 状态的任务>
   - 真实性锚点：<是否已有最小真实闭环，或仍停留在替身/unknown>

4. **推荐下一步**
   - 基于 Artifact 状态和阶段判断
   - 若 spec.md / design.md 可能 stale 或 conflicting，但原因需要统一校准，优先推荐 `/ark:ark-sync`
   - 若 spec.md / design.md 的更新原因已经明确，可推荐 `/ark:ark-spec` 或 `/ark:ark-design`
   - 若专题方案、接口契约、集成或数据源元信息缺失/过期，可推荐 `/ark:ark-solution`
   - 若 tasks 推进较多但真实锚点仍缺失，优先推荐 `/ark:ark-sync` 或 `/ark:ark-plan`
   - 给出 1-2 个推荐，附理由
   - 等用户选择后激活对应 Skill

## 验证要求

- 状态判断必须基于 Artifact 实际内容，不得猜测
- 可信度判断遵循 rules/artifact-roles.md 的四态定义
- 推荐必须是 ARK 已定义的合法 Skill
- 不得把 mock/fake/in-memory/合成数据状态描述为真实闭环完成
- 不得自动执行任何后续 Skill
- 不得更新任何 Artifact

## 停止条件

- 已输出状态报告和推荐
- 用户的问题已被回答

## 固定输出格式

### 1. 项目状态

- 当前阶段：<初始化/规划/实施/验证/收尾>
- Artifact 可信度：<列出非 fresh 的 Artifact 及判断依据>
- 活跃任务：<Doing 状态的任务列表>
- 阻塞项：<Blocked 状态的任务列表>
- 真实性锚点：<真实入口 / 真实依赖 / 数据源 / 契约状态>

### 2. 推荐下一步

- 推荐选项 A：`/ark:ark-xxx` — <理由>
- 推荐选项 B：`/ark:ark-xxx` — <理由>（可选）

### 3. 边界声明

本次仅提供状态读取和路径推荐，不会自动执行后续 Skill。

## 备注

/ark:ark 是辅助入口。日常使用中，rules/ark.md 的自动路由倾向会在你描述任务时自动引导到合适的 Skill。本 Skill 适合在不确定、接手项目、或想查看整体进度时使用。
